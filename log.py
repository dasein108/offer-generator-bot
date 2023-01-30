import logging
import os
import traceback
from logging.handlers import RotatingFileHandler
from typing import Any, Optional

LOG_FORMAT = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"


def append_formatter(handler: Any, logging_level: Any = logging.INFO, log_format: str = LOG_FORMAT):
    handler.setLevel(logging_level)
    handler.setFormatter(logging.Formatter(log_format))
    return handler


def setup_logger(log_name: Optional[str] = None, logging_level: Any = logging.INFO, log_format: str = LOG_FORMAT):
    logger = logging.getLogger(log_name)
    logger.setLevel(logging_level)
    if log_name is not None:
        file_name = os.path.expanduser(f"{log_name}.log")

        logger.addHandler(append_formatter(RotatingFileHandler(file_name, maxBytes=1000000, backupCount=3),
                                           logging_level, log_format=log_format))

    logger.addHandler(append_formatter(logging.StreamHandler(), logging_level, log_format=log_format))

    return logger
