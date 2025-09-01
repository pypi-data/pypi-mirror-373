"""Utility functions for UX."""

import contextlib
import enum
import os
import sys
import traceback
import typing
from typing import Callable, List, Optional, Union

import colorama
import rich.console as rich_console

from konduktor import config
from konduktor import logging as konduktor_logging

if typing.TYPE_CHECKING:
    import pathlib

console = rich_console.Console()

INDENT_SYMBOL = f'{colorama.Style.DIM}├── {colorama.Style.RESET_ALL}'
INDENT_LAST_SYMBOL = f'{colorama.Style.DIM}└── {colorama.Style.RESET_ALL}'

# Console formatting constants
BOLD = '\033[1m'
RESET_BOLD = '\033[0m'

# Log path hint in the spinner during launching
_LOG_PATH_HINT = (
    f'{colorama.Style.DIM}View logs at: {{log_path}}' f'{colorama.Style.RESET_ALL}'
)


def console_newline():
    """Prints a newline to the console using rich.

    Useful when catching exceptions inside console.status()
    """
    console.print()


@contextlib.contextmanager
def print_exception_no_traceback():
    """A context manager that prints out an exception without traceback.

    Mainly for UX: user-facing errors, e.g., ValueError, should suppress long
    tracebacks.

    If KONDUKTOR_DEBUG environment variable is set, this context manager is a
    no-op and the full traceback will be shown.

    Example usage:

        with print_exception_no_traceback():
            if error():
                raise ValueError('...')
    """
    if os.environ.get('KONDUKTOR_DEBUG'):
        # When KONDUKTOR_DEBUG is set, show the full traceback
        yield
    else:
        original_tracelimit = getattr(sys, 'tracebacklimit', 1000)
        sys.tracebacklimit = 0
        yield
        sys.tracebacklimit = original_tracelimit


@contextlib.contextmanager
def enable_traceback():
    """Reverts the effect of print_exception_no_traceback().

    This is used for usage_lib to collect the full traceback.
    """
    original_tracelimit = getattr(sys, 'tracebacklimit', 1000)
    sys.tracebacklimit = 1000
    yield
    sys.tracebacklimit = original_tracelimit


class RedirectOutputForProcess:
    """Redirects stdout and stderr to a file.

    This class enabled output redirect for multiprocessing.Process.
    Example usage:

    p = multiprocessing.Process(
        target=RedirectOutputForProcess(func, file_name).run, args=...)

    This is equal to:

    p = multiprocessing.Process(target=func, args=...)

    Plus redirect all stdout/stderr to file_name.
    """

    def __init__(self, func: Callable, file: str, mode: str = 'w') -> None:
        self.func = func
        self.file = file
        self.mode = mode

    def run(self, *args, **kwargs):
        with open(self.file, self.mode, encoding='utf-8') as f:
            sys.stdout = f
            sys.stderr = f
            # reconfigure logger since the logger is initialized before
            # with previous stdout/stderr
            konduktor_logging.reload_logger()
            logger = konduktor_logging.init_logger(__name__)
            # The subprocess_util.run('konduktor status') inside
            # konduktor.execution::_execute cannot be redirect, since we cannot
            # directly operate on the stdout/stderr of the subprocess. This
            # is because some code in konduktor will specify the stdout/stderr
            # of the subprocess.
            try:
                self.func(*args, **kwargs)
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f'Failed to run {self.func.__name__}. ' f'Details: {e}')
                with enable_traceback():
                    logger.error(f'  Traceback:\n{traceback.format_exc()}')
                raise


def log_path_hint(log_path: Union[str, 'pathlib.Path']) -> str:
    """Gets the log path hint for the given log path."""
    log_path = str(log_path)
    expanded_home = os.path.expanduser('~')
    if log_path.startswith(expanded_home):
        log_path = '~' + log_path[len(expanded_home) :]
    return _LOG_PATH_HINT.format(log_path=log_path)


def starting_message(message: str) -> str:
    """Gets the starting message for the given message."""
    # We have to reset the color before the message, because sometimes if a
    # previous spinner with dimmed color overflows in a narrow terminal, the
    # color might be messed up.
    return f'{colorama.Style.RESET_ALL}⚙︎ {message}'


def finishing_message(
    message: str, log_path: Optional[Union[str, 'pathlib.Path']] = None
) -> str:
    """Gets the finishing message for the given message."""
    # We have to reset the color before the message, because sometimes if a
    # previous spinner with dimmed color overflows in a narrow terminal, the
    # color might be messed up.
    success_prefix = (
        f'{colorama.Style.RESET_ALL}{colorama.Fore.GREEN}✓ '
        f'{message}{colorama.Style.RESET_ALL}'
    )
    if log_path is None:
        return success_prefix
    path_hint = log_path_hint(log_path)
    return f'{success_prefix}  {path_hint}'


def error_message(
    message: str, log_path: Optional[Union[str, 'pathlib.Path']] = None
) -> str:
    """Gets the error message for the given message."""
    # We have to reset the color before the message, because sometimes if a
    # previous spinner with dimmed color overflows in a narrow terminal, the
    # color might be messed up.
    error_prefix = (
        f'{colorama.Style.RESET_ALL}{colorama.Fore.RED}⨯'
        f'{colorama.Style.RESET_ALL} {message}'
    )
    if log_path is None:
        return error_prefix
    path_hint = log_path_hint(log_path)
    return f'{error_prefix}  {path_hint}'


def retry_message(message: str) -> str:
    """Gets the retry message for the given message."""
    # We have to reset the color before the message, because sometimes if a
    # previous spinner with dimmed color overflows in a narrow terminal, the
    # color might be messed up.
    return (
        f'{colorama.Style.RESET_ALL}{colorama.Fore.YELLOW}↺'
        f'{colorama.Style.RESET_ALL} {message}'
    )


def spinner_message(
    message: str, log_path: Optional[Union[str, 'pathlib.Path']] = None
) -> str:
    """Gets the spinner message for the given message and log path."""
    colored_spinner = f'[bold cyan]{message}[/]'
    if log_path is None:
        return colored_spinner
    path_hint = log_path_hint(log_path)
    return f'{colored_spinner}  {path_hint}'


class CommandHintType(enum.Enum):
    JOB = 'JOB'
    JOB_STOP = 'JOB_STOP'


def command_hint_messages(
    hint_type: CommandHintType,
    job_id: Union[str, List[str]],
) -> str:
    """Gets the command hint messages for the given job id."""
    hint_str = '\n📋 Useful Commands'
    if hint_type == CommandHintType.JOB:
        job_hint_str = (
            f'\nJob ID: {job_id}'
            f'\n{INDENT_SYMBOL}To stream job logs:\t\t'
            f'{BOLD}konduktor logs {job_id} {RESET_BOLD}'
            f'\n{INDENT_SYMBOL}To list all jobs:\t\t'
            f'{BOLD}konduktor status{RESET_BOLD}'
            f'\n{INDENT_SYMBOL}To suspend the job:\t\t'
            f'{BOLD}konduktor stop {job_id} {RESET_BOLD}'
            f'\n{INDENT_SYMBOL}{colorama.Fore.RED}To delete the job:\t\t'
            f'{BOLD}konduktor down {job_id} {RESET_BOLD}{colorama.Style.RESET_ALL}'
        )
        hint_str += f'{job_hint_str}'
    elif hint_type == CommandHintType.JOB_STOP:
        assert isinstance(job_id, list), 'job_id must be a list of strings'
        job_ids_str = ' '.join(job_id)
        hint_str += (
            f'\n{INDENT_SYMBOL}To resume the following jobs:\t\t'
            f'{BOLD}konduktor start {job_ids_str} {RESET_BOLD}'
        )
    else:
        raise ValueError(f'Invalid hint type: {hint_type}')

    if config.get_nested(('tailscale', 'secret_name'), None) is not None:
        hint_str += (
            f'\n{INDENT_SYMBOL}To tailscale ssh:\t\t'
            f'{BOLD}ssh root@{job_id}-workers-0-0 {RESET_BOLD}'
        )
    return hint_str
