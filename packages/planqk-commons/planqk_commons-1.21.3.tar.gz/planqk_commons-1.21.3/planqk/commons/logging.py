import logging
import os
import sys

from loguru import logger

from planqk.commons.constants import LOG_LEVEL_ENV, DEFAULT_LOG_LEVEL


class LogHandler(logging.Handler):
    """
    A handler class which allows for the use of Loguru with the standard logging module.
    """

    def __init__(self, name: str = None) -> None:
        if name is not None:
            self._logger = logger.patch(lambda record: record.update(name=name))
        else:
            self._logger = logger
        super().__init__()

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        self._logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def init_logging():
    """
    Initialize the logging configuration. The logging level is set to the value of the LOG_LEVEL environment variable.
    """
    logging_level = os.environ.get(LOG_LEVEL_ENV, DEFAULT_LOG_LEVEL).upper()

    logging.getLogger().handlers = [LogHandler()]
    logging.getLogger().setLevel(logging_level)

    logger.configure(handlers=[{"sink": sys.stdout, "level": logging_level}])

    for stdlib_logger, loguru_handler in (
        (logging.getLogger(name), LogHandler(name))
        for name in logging.root.manager.loggerDict
    ):
        stdlib_logger.handlers = [loguru_handler]
        stdlib_logger.propagate = False
