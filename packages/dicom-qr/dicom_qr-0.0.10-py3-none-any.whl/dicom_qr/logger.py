from __future__ import annotations
import logging.handlers

import loguru
from loguru import logger
from rich.console import Console

ENABLE_FILE_LOGGING = True


console = Console()


# https://github.com/Textualize/rich/issues/2416
def _log_formatter(record: loguru.Record) -> str:
    """Log message formatter"""
    color_map = {
        'TRACE': 'dim blue',
        'DEBUG': 'cyan',
        'INFO': 'bold',
        'SUCCESS': 'bold green',
        'WARNING': 'yellow',
        'ERROR': 'bold red',
        'CRITICAL': 'bold white on red'
    }
    lvl_color = color_map.get(record['level'].name, 'cyan')
    return (
        '[not bold green]{time:YYYY/MM/DD HH:mm:ss}[/not bold green] | {level.icon} | {name}'
         f'  - [{lvl_color}]{{message}}[/{lvl_color}]'
    )


def setup_logging(log_level: int = logging.INFO, dicom_log_level: int = logging.WARNING) -> None:
    """ Setup logging. """
    logger.remove()

    # change handler for default loggers
    logging.getLogger('pynetdicom').setLevel(dicom_log_level)
    logging.getLogger('pynetdicom').handlers = [InterceptHandler(level=dicom_log_level)]
    logging.getLogger('py.warnings').handlers = [InterceptHandler(level=logging.WARNING)]

    logger.add(
        console.print,
        level=log_level,
        format=_log_formatter,
        colorize=True,
    )

    if ENABLE_FILE_LOGGING:
        logger.add('dicom_qr_{time:%Y%m%d}.log', rotation='00:01', level='TRACE',
                   format='{time:%Y-%m-%d_%H:%M:%S.%f} | {level.icon} | {message} | {name}:{file}:{function}[{line}]')
        logger.add('dicom_qr_{time:%Y%m%d}.jsonl', serialize=True, rotation='00:01', level='TRACE')


# https://gist.github.com/nkhitrov/a3e31cfcc1b19cba8e1b626276148c49
class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        """ Copy the log message from logging module to loguru. """
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelname

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage(), name=record.name)
