"""Logging utilities."""

import contextlib
import logging
import os
import threading
from datetime import datetime

import colorama

from konduktor import constants

CHECK_MARK_EMOJI = '\U00002714'  # Heavy check mark unicode
PARTY_POPPER_EMOJI = '\U0001f389'  # Party popper unicode

_FORMAT = '[%(levelname).1s %(asctime)s %(filename)s:%(lineno)d] %(message)s'
_DATE_FORMAT = '%m-%d %H:%M:%S'

_logging_config = threading.local()
_log_path = None


class NewLineFormatter(logging.Formatter):
    """Adds logging prefix to newlines to align multi-line messages."""

    def __init__(self, fmt, datefmt=None, dim=False):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.dim = dim

    def format(self, record):
        msg = logging.Formatter.format(self, record)
        if record.message != '':
            parts = msg.partition(record.message)
            msg = msg.replace('\n', '\r\n' + parts[0])
            if self.dim:
                msg = colorama.Style.DIM + msg + colorama.Style.RESET_ALL
        return msg


FORMATTER = NewLineFormatter(_FORMAT, datefmt=_DATE_FORMAT)


@contextlib.contextmanager
def set_logging_level(logger: str, level: int):
    logger = logging.getLogger(logger)
    original_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(original_level)


def get_logger(name: str):
    global _log_path

    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)  # Always capture all levels internally

    # --- File logging: Always enabled ---
    if not _log_path:
        log_dir = os.path.expanduser('~/.konduktor/logs')
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        _log_path = os.path.join(log_dir, f'konduktor-logs-{timestamp}.log')
        print(f'Log file: {_log_path}')

    fh = logging.FileHandler(_log_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(FORMATTER)
    logger.addHandler(fh)

    # --- Console logging: INFO level by default, DEBUG if KONDUKTOR_DEBUG=1 ---
    ch = logging.StreamHandler()
    if os.environ.get('KONDUKTOR_DEBUG') == '1':
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    ch.setFormatter(FORMATTER)
    logger.addHandler(ch)

    logger.propagate = False
    return logger


def is_silent():
    if not hasattr(_logging_config, 'is_silent'):
        # Should not set it globally, as the global assignment
        # will be executed only once if the module is imported
        # in the main thread, and will not be executed in other
        # threads.
        _logging_config.is_silent = False
    return _logging_config.is_silent


def get_run_timestamp() -> str:
    return 'konduktor-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')


def generate_tmp_logging_file_path(file_name: str) -> str:
    """Generate an absolute path of a tmp file for logging."""
    run_timestamp = get_run_timestamp()
    log_dir = os.path.join(constants.KONDUKTOR_LOGS_DIRECTORY, run_timestamp)
    log_path = os.path.expanduser(os.path.join(log_dir, file_name))

    return log_path
