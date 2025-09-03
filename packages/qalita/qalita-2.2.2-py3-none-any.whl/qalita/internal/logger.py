"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import logging
import sys
import os
from pprint import pformat
from loguru import logger

if os.getenv("QALITA_DEBUG"):
    LOGURU_FORMAT = "<cyan>QALITA Agent</cyan> | {time:DD-MM-YYYY - HH:mm:ss.SSS} | <level>{level: <8}</level> | <magenta>{name: <8}</magenta>:<magenta>{function}</magenta>:<magenta>{line}</magenta> | <level>{message}</level>"
else:
    LOGURU_FORMAT = "<level>{message}</level>"


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
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

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


def init_logging():
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("*")
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    # set logs output, level and format
    logger.configure(
        handlers=[{"sink": sys.stdout, "level": logging.DEBUG, "format": format_record}]
    )

    return logger
