# Proprietary Changes made for Trainy under the Trainy Software License
# Original source: skypilot: https://github.com/skypilot-org/skypilot
# which is Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility functions for subprocesses."""

import os
import resource
import subprocess
from multiprocessing import pool
from typing import Any, Callable, Dict, List, Optional, Union

import colorama
import psutil

from konduktor import constants, logging
from konduktor.utils import exceptions, log_utils, ux_utils

logger = logging.get_logger(__name__)

_fd_limit_warning_shown = False


def run(cmd, **kwargs):
    # Should be careful to use this function, as the child process cmd spawn may
    # keep running in the background after the current program is killed. To get
    # rid of this problem, use `log_utils.run_with_log`.
    shell = kwargs.pop('shell', True)
    check = kwargs.pop('check', True)
    executable = kwargs.pop('executable', '/bin/bash')
    if not shell:
        executable = None
    return subprocess.run(
        cmd, shell=shell, check=check, executable=executable, **kwargs
    )


def run_no_outputs(cmd, **kwargs):
    return run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)


def _get_thread_multiplier(cloud_str: Optional[str] = None) -> int:
    # If using Kubernetes, we use 4x the number of cores.
    if cloud_str and cloud_str.lower() == 'kubernetes':
        return 4
    return 1


def get_max_workers_for_file_mounts(
    common_file_mounts: Dict[str, str], cloud_str: Optional[str] = None
) -> int:
    global _fd_limit_warning_shown
    fd_limit, _ = resource.getrlimit(resource.RLIMIT_NOFILE)

    # Raise warning for low fd_limit (only once)
    if fd_limit < 1024 and not _fd_limit_warning_shown:
        logger.warning(
            f'Open file descriptor limit ({fd_limit}) is low. File sync to '
            'remote clusters may be slow. Consider increasing the limit using '
            '`ulimit -n <number>` or modifying system limits.'
        )
        _fd_limit_warning_shown = True

    fd_per_rsync = 5
    for src in common_file_mounts.values():
        if os.path.isdir(src):
            # Assume that each file/folder under src takes 5 file descriptors
            # on average.
            fd_per_rsync = max(fd_per_rsync, len(os.listdir(src)) * 5)

    # Reserve some file descriptors for the system and other processes
    fd_reserve = 100

    max_workers = (fd_limit - fd_reserve) // fd_per_rsync
    # At least 1 worker, and avoid too many workers overloading the system.
    num_threads = get_parallel_threads(cloud_str)
    max_workers = min(max(max_workers, 1), num_threads)
    logger.debug(f'Using {max_workers} workers for file mounts.')
    return max_workers


def get_parallel_threads(cloud_str: Optional[str] = None) -> int:
    """Returns the number of threads to use for parallel execution.

    Args:
        cloud_str: The cloud
    """
    cpu_count = os.cpu_count()
    if cpu_count is None:
        cpu_count = 1
    return max(4, cpu_count - 1) * _get_thread_multiplier(cloud_str)


def run_in_parallel(
    func: Callable, args: List[Any], num_threads: Optional[int] = None
) -> List[Any]:
    """Run a function in parallel on a list of arguments.

    Args:
        func: The function to run in parallel
        args: Iterable of arguments to pass to func
        num_threads: Number of threads to use. If None, uses
          get_parallel_threads()

    Returns:
      A list of the return values of the function func, in the same order as the
        arguments.

    Raises:
        Exception: The first exception encountered.
    """
    # Short-circuit for short lists
    if len(args) == 0:
        return []
    if len(args) == 1:
        return [func(args[0])]

    processes = num_threads if num_threads is not None else get_parallel_threads()

    with pool.ThreadPool(processes=processes) as p:
        ordered_iterators = p.imap(func, args)
        return list(ordered_iterators)


def handle_returncode(
    returncode: int,
    command: str,
    error_msg: Union[str, Callable[[], str]],
    stderr: Optional[str] = None,
    stream_logs: bool = True,
) -> None:
    """Handle the returncode of a command.

    Args:
        returncode: The returncode of the command.
        command: The command that was run.
        error_msg: The error message to print.
        stderr: The stderr of the command.
        stream_logs: Whether to stream logs.
    """
    echo = logger.error if stream_logs else logger.debug
    if returncode != 0:
        if stderr is not None:
            echo(stderr)

        if callable(error_msg):
            error_msg = error_msg()
        format_err_msg = f'{colorama.Fore.RED}{error_msg}{colorama.Style.RESET_ALL}'
        with ux_utils.print_exception_no_traceback():
            raise exceptions.CommandError(returncode, command, format_err_msg, stderr)


def kill_children_processes(
    parent_pids: Optional[Union[int, List[Optional[int]]]] = None, force: bool = False
) -> None:
    """Kill children processes recursively.

    We need to kill the children, so that
    1. The underlying subprocess will not print the logs to the terminal,
       after this program exits.
    2. The underlying subprocess will not continue with starting a cluster
       etc. while we are cleaning up the clusters.

    Args:
        parent_pids: Optional PIDs of a series of processes. The processes and
          their children will be killed.  If a list of PID is specified, it is
          killed by the order in the list. This is for guaranteeing the order
          of cleaning up and suppress flaky errors.
        force: bool, send SIGKILL if force, otherwise, use SIGTERM for
          gracefully kill the process.
    """
    if isinstance(parent_pids, int):
        parent_pids = [parent_pids]

    def kill(proc: psutil.Process):
        if not proc.is_running():
            # Skip if the process is not running.
            return
        logger.debug(f'Killing process {proc.pid}')
        try:
            if force:
                proc.kill()
            else:
                proc.terminate()
            proc.wait(timeout=10)
        except psutil.NoSuchProcess:
            # The child process may have already been terminated.
            pass
        except psutil.TimeoutExpired:
            logger.debug(f'Process {proc.pid} did not terminate after 10 seconds')
            # Attempt to force kill if the normal termination fails
            if not force:
                logger.debug(f'Force killing process {proc.pid}')
                proc.kill()
                proc.wait(timeout=5)  # Shorter timeout after force kill

    parent_processes = []
    if parent_pids is None:
        parent_processes = [psutil.Process()]
    else:
        for pid in parent_pids:
            try:
                process = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue
            parent_processes.append(process)

    for parent_process in parent_processes:
        child_processes = parent_process.children(recursive=True)
        if parent_pids is not None:
            kill(parent_process)
        logger.debug(f'Killing child processes: {child_processes}')
        for child in child_processes:
            kill(child)


def kill_process_daemon(process_pid: int) -> None:
    """Start a daemon as a safety net to kill the process.

    Args:
        process_pid: The PID of the process to kill.
    """
    # Get initial children list
    try:
        process = psutil.Process(process_pid)
        initial_children = [p.pid for p in process.children(recursive=True)]
    except psutil.NoSuchProcess:
        initial_children = []

    parent_pid = os.getpid()
    daemon_script = os.path.join(
        os.path.dirname(os.path.abspath(log_utils.__file__)), 'subprocess_daemon.py'
    )
    python_path = subprocess.check_output(
        constants.GET_PYTHON_PATH_CMD,
        shell=True,
        stderr=subprocess.DEVNULL,
        encoding='utf-8',
    ).strip()
    daemon_cmd = [
        python_path,
        daemon_script,
        '--parent-pid',
        str(parent_pid),
        '--proc-pid',
        str(process_pid),
        # We pass the initial children list to avoid the race condition where
        # the process_pid is terminated before the daemon starts and gets the
        # children list.
        '--initial-children',
        ','.join(map(str, initial_children)),
    ]

    # We do not need to set `start_new_session=True` here, as the
    # daemon script will detach itself from the parent process with
    # fork to avoid being killed by parent process. See the reason we
    # daemonize the process in `sky/skylet/subprocess_daemon.py`.
    subprocess.Popen(
        daemon_cmd,
        # Suppress output
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        # Disable input
        stdin=subprocess.DEVNULL,
    )
