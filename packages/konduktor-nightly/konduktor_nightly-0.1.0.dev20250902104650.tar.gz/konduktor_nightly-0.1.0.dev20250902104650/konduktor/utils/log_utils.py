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

import asyncio
import copy
import enum
import io
import json
import multiprocessing
import os
import subprocess
import sys
import types
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import colorama
import kr8s
import prettytable
import requests
import websockets

from konduktor import config, logging
from konduktor.utils import kubernetes_utils, subprocess_utils

logger = logging.get_logger(__name__)


LOKI_REMOTE_PORT = 3100
WEBSOCKET_TIMEOUT = 10
INFINITY = 999999
VICKY_REMOTE_PORT = 9428


class LogBackend(enum.Enum):
    VICTORIA = 'victoria'
    LOKI = 'loki'


class LineProcessor(object):
    """A processor for log lines."""

    def __enter__(self) -> None:
        pass

    def process_line(self, log_line: str) -> None:
        pass

    def __exit__(
        self,
        except_type: Optional[Type[BaseException]],
        except_value: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ) -> None:
        del except_type, except_value, traceback  # unused
        pass


class _ProcessingArgs:
    """Arguments for processing logs."""

    def __init__(
        self,
        log_path: str,
        stream_logs: bool,
        start_streaming_at: str = '',
        end_streaming_at: Optional[str] = None,
        skip_lines: Optional[List[str]] = None,
        replace_crlf: bool = False,
        line_processor: Optional[LineProcessor] = None,
        streaming_prefix: Optional[str] = None,
    ) -> None:
        self.log_path = log_path
        self.stream_logs = stream_logs
        self.start_streaming_at = start_streaming_at
        self.end_streaming_at = end_streaming_at
        self.skip_lines = skip_lines
        self.replace_crlf = replace_crlf
        self.line_processor = line_processor
        self.streaming_prefix = streaming_prefix


def _handle_io_stream(io_stream, out_stream, args: _ProcessingArgs):
    """Process the stream of a process."""
    out_io = io.TextIOWrapper(
        io_stream, encoding='utf-8', newline='', errors='replace', write_through=True
    )

    start_streaming_flag = False
    end_streaming_flag = False
    streaming_prefix = args.streaming_prefix if args.streaming_prefix else ''
    line_processor = (
        LineProcessor() if args.line_processor is None else args.line_processor
    )

    out = []
    with open(args.log_path, 'a', encoding='utf-8') as fout:
        with line_processor:
            while True:
                line = out_io.readline()
                if not line:
                    break
                # start_streaming_at logic in processor.process_line(line)
                if args.replace_crlf and line.endswith('\r\n'):
                    # Replace CRLF with LF to avoid ray logging to the same
                    # line due to separating lines with '\n'.
                    line = line[:-2] + '\n'
                if args.skip_lines is not None and any(
                    skip in line for skip in args.skip_lines
                ):
                    continue
                if args.start_streaming_at in line:
                    start_streaming_flag = True
                if args.end_streaming_at is not None and args.end_streaming_at in line:
                    # Keep executing the loop, only stop streaming.
                    # saving them in log files.
                    end_streaming_flag = True
                if args.stream_logs and start_streaming_flag and not end_streaming_flag:
                    print(streaming_prefix + line, end='', file=out_stream, flush=True)
                if args.log_path != '/dev/null':
                    fout.write(line)
                    fout.flush()
                line_processor.process_line(line)
                out.append(line)
    return ''.join(out)


def process_subprocess_stream(proc, args: _ProcessingArgs) -> Tuple[str, str]:
    """Redirect the process's filtered stdout/stderr to both stream and file"""
    if proc.stderr is not None:
        # Asyncio does not work as the output processing can be executed in a
        # different thread.
        # selectors is possible to handle the multiplexing of stdout/stderr,
        # but it introduces buffering making the output not streaming.
        with multiprocessing.pool.ThreadPool(processes=1) as pool:
            err_args = copy.copy(args)
            err_args.line_processor = None
            stderr_fut = pool.apply_async(
                _handle_io_stream, args=(proc.stderr, sys.stderr, err_args)
            )
            # Do not launch a thread for stdout as the rich.status does not
            # work in a thread, which is used in
            # log_utils.RayUpLineProcessor.
            stdout = _handle_io_stream(proc.stdout, sys.stdout, args)
            stderr = stderr_fut.get()
    else:
        stdout = _handle_io_stream(proc.stdout, sys.stdout, args)
        stderr = ''
    return stdout, stderr


def create_table(field_names: List[str], **kwargs) -> prettytable.PrettyTable:
    """Creates table with default style."""
    border = kwargs.pop('border', False)
    align = kwargs.pop('align', 'l')
    table = prettytable.PrettyTable(
        align=align, border=border, field_names=field_names, **kwargs
    )
    table.left_padding_width = 0
    table.right_padding_width = 2
    return table


def run_with_log(
    cmd: Union[List[str], str],
    log_path: str,
    *,
    require_outputs: bool = False,
    stream_logs: bool = False,
    start_streaming_at: str = '',
    end_streaming_at: Optional[str] = None,
    skip_lines: Optional[List[str]] = None,
    shell: bool = False,
    with_ray: bool = False,
    process_stream: bool = True,
    line_processor: Optional[LineProcessor] = None,
    streaming_prefix: Optional[str] = None,
    **kwargs,
) -> Union[int, Tuple[int, str, str]]:
    """Runs a command and logs its output to a file.

    Args:
        cmd: The command to run.
        log_path: The path to the log file.
        stream_logs: Whether to stream the logs to stdout/stderr.
        require_outputs: Whether to return the stdout/stderr of the command.
        process_stream: Whether to post-process the stdout/stderr of the
            command, such as replacing or skipping lines on the fly. If
            enabled, lines are printed only when '\r' or '\n' is found.

    Returns the returncode or returncode, stdout and stderr of the command.
      Note that the stdout and stderr is already decoded.
    """
    assert process_stream or not require_outputs, (
        process_stream,
        require_outputs,
        'require_outputs should be False when process_stream is False',
    )

    log_path = os.path.expanduser(log_path)
    dirname = os.path.dirname(log_path)
    os.makedirs(dirname, exist_ok=True)
    # Redirect stderr to stdout when using ray, to preserve the order of
    # stdout and stderr.
    stdout_arg = stderr_arg = None
    if process_stream:
        stdout_arg = subprocess.PIPE
        stderr_arg = subprocess.PIPE if not with_ray else subprocess.STDOUT
    # Use stdin=subprocess.DEVNULL by default, as allowing inputs will mess up
    # the terminal output when typing in the terminal that starts the API
    # server.
    stdin = kwargs.pop('stdin', subprocess.DEVNULL)
    with subprocess.Popen(
        cmd,
        stdout=stdout_arg,
        stderr=stderr_arg,
        start_new_session=True,
        shell=shell,
        stdin=stdin,
        **kwargs,
    ) as proc:
        try:
            subprocess_utils.kill_process_daemon(proc.pid)
            stdout = ''
            stderr = ''

            if process_stream:
                if skip_lines is None:
                    skip_lines = []
                # Skip these lines caused by `-i` option of bash. Failed to
                # find other way to turn off these two warning.
                # https://stackoverflow.com/questions/13300764/how-to-tell-bash-not-to-issue-warnings-cannot-set-terminal-process-group-and # noqa: E501
                # `ssh -T -i -tt` still cause the problem.
                skip_lines += [
                    'bash: cannot set terminal process group',
                    'bash: no job control in this shell',
                ]
                # We need this even if the log_path is '/dev/null' to ensure the
                # progress bar is shown.
                # NOTE: Lines are printed only when '\r' or '\n' is found.
                args = _ProcessingArgs(
                    log_path=log_path,
                    stream_logs=stream_logs,
                    start_streaming_at=start_streaming_at,
                    end_streaming_at=end_streaming_at,
                    skip_lines=skip_lines,
                    line_processor=line_processor,
                    # Replace CRLF when the output is logged to driver by ray.
                    replace_crlf=with_ray,
                    streaming_prefix=streaming_prefix,
                )
                stdout, stderr = process_subprocess_stream(proc, args)
            proc.wait()
            if require_outputs:
                return proc.returncode, stdout, stderr
            return proc.returncode
        except KeyboardInterrupt:
            # Kill the subprocess directly, otherwise, the underlying
            # process will only be killed after the python program exits,
            # causing the stream handling stuck at `readline`.
            subprocess_utils.kill_children_processes()
            raise


async def _read_logs(url: str, timeout: int, job_name: str, worker_id: int, port: int):
    ws = await asyncio.wait_for(websockets.connect(url), timeout=WEBSOCKET_TIMEOUT)
    logger.info(
        f'{colorama.Fore.YELLOW}Tailing logs. '
        f'Forwarding from remote port {port}. Press Ctrl+C to stop. '
        f'{colorama.Style.RESET_ALL}'
    )
    try:
        while True:
            message = await asyncio.wait_for(ws.recv(), timeout=timeout)
            try:
                payload = json.loads(message)
                for stream in payload['streams']:
                    if stream['values'][0][1] is not None:
                        print(
                            f"{colorama.Fore.CYAN}{colorama.Style.BRIGHT} "
                            f"(job_name={job_name} worker_id={worker_id})"
                            f"{colorama.Style.RESET_ALL} {stream['values'][0][1]}",
                            flush=True,
                        )
            except json.JSONDecodeError:
                logger.warning(f'Failed to decode log skipping: {message}')
                logger.debug(f'Dropped log: {message}')
                continue
    except asyncio.exceptions.TimeoutError:
        logger.debug('Websocket timed-out, closing log stream!')
    except KeyboardInterrupt:
        logger.debug('Keyboard interrupt, closing log stream!')


def tail_loki_logs_ws(
    job_name: str, worker_id: int = 0, num_logs: int = 1000, follow: bool = True
):
    if num_logs > 5000:
        # TODO(asaiacai): we should not have a limit on the number of logs, but rather
        # let the user specify any number of lines, and we can print the last N lines.
        # this can be done in chunks. Potentially, we can query range
        # until we reach the end of the log and then invoke tail again.
        # Also include checks that the job is running/ever ran.
        raise ValueError('num_logs must be less than or equal to 5000')
    loki_svc = kr8s.objects.Service.get('loki', namespace='loki')
    with kr8s.portforward.PortForward(
        loki_svc, LOKI_REMOTE_PORT, local_port='auto'
    ) as port:
        loki_url = f'ws://localhost:{port}/loki/api/v1/tail'
        logger.debug(f'Loki URL: {loki_url}')
        params = {
            'query': urllib.parse.quote(
                r'{' + f'k8s_job_name="{job_name}-workers-0",'
                r' k8s_container_name="konduktor-container"} '
                f' | batch_kubernetes_io_job_completion_index = `{worker_id}`'
            ),
            'limit': num_logs,
            'delay': 5,
            # TODO(asaiacai): need to auto-generate the start and end times.
        }

        query_string = '&'.join(f'{key}={value}' for key, value in params.items())
        loki_url += f'?{query_string}'
        timeout = INFINITY if follow else WEBSOCKET_TIMEOUT
        asyncio.run(
            _read_logs(loki_url, timeout, job_name, worker_id, LOKI_REMOTE_PORT)
        )


def tail_vicky_logs(
    job_name: str,
    worker_id: int = 0,
    num_logs: int = -1,
    follow: bool = True,
):
    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)
    query: Dict[str, Any] = {}
    vicky_svc = kr8s.objects.Service.get(
        'vls-victoria-logs-single-server', namespace='victoria-logs'
    )

    if num_logs == -1:
        query = {}
    else:
        assert num_logs > 0, f'num_logs must be greater than 0, got {num_logs}'
        query = {'limit': num_logs}
    if follow:
        logger.info(
            'Tailing logs from 1 hour ago. '
            'If logs come up empty, there might be logs just earlier '
            'than the past hour, check Grafana or use:\n'
            f'{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}'
            f'`konduktor logs --no-follow {job_name}`'
            f'{colorama.Style.RESET_ALL}'
        )
        query['start_offset'] = '1h'
    query['query'] = (
        f'k8s.namespace.name: "{namespace}" AND '
        f'batch.kubernetes.io/job-name: "{job_name}-workers-0" AND '
        f'batch.kubernetes.io/job-completion-index: "{worker_id}"'
    )

    with kr8s.portforward.PortForward(
        vicky_svc, VICKY_REMOTE_PORT, local_port='auto'
    ) as port:
        if follow:
            timeout = INFINITY
            vicky_url = f'http://localhost:{port}/select/logsql/tail'
        else:
            vicky_url = f'http://localhost:{port}/select/logsql/query'
            timeout = 5
        logger.debug(f'Vicky URL: {vicky_url}')

        try:
            logger.debug(f'Making request to {vicky_url} with query: {query}')
            with requests.post(
                vicky_url, data=query, stream=True, timeout=timeout
            ) as response:  # type: requests.Response
                logger.debug(f'Response status: {response.status_code}')
                if response.status_code != 200:
                    logger.error(
                        f'VictoriaLogs API returned status {response.status_code}: '
                        f'{response.text}'
                    )
                    return

                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        payload = json.loads(line)
                        if 'missing _msg field' in payload['_msg']:
                            payload['_msg'] = ''
                        print(
                            f"{colorama.Fore.CYAN}{colorama.Style.BRIGHT} "
                            f"(job_name={job_name} worker_id={worker_id})"
                            f"{colorama.Style.RESET_ALL} {payload['_msg']}",
                            flush=True,
                        )

        except KeyboardInterrupt:
            logger.info('\nStopping log stream...')
        except requests.exceptions.Timeout:
            logger.error(f'Request to VictoriaLogs timed out after {timeout} seconds')
        except requests.exceptions.ConnectionError as e:
            logger.error(f'Failed to connect to VictoriaLogs at {vicky_url}: {e}')
        except requests.exceptions.RequestException as e:
            logger.error(f'Request to VictoriaLogs failed: {e}')
        except Exception as e:
            logger.error(f'Unexpected error while tailing VictoriaLogs: {e}')


def tail_logs(
    job_name: str,
    worker_id: int = 0,
    num_logs: int = 1000,
    follow: bool = True,
):
    logs_backend = config.get_nested(('logs', 'backend'), None)
    if logs_backend == LogBackend.VICTORIA:
        tail_vicky_logs(job_name, worker_id, num_logs, follow)
    elif logs_backend == LogBackend.LOKI:
        tail_loki_logs_ws(job_name, worker_id, num_logs, follow)
    else:
        logger.info('Defaulting to VictoriaLogs')
        tail_vicky_logs(job_name, worker_id, num_logs, follow)
