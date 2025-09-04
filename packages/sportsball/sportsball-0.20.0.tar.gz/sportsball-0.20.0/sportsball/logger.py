"""Functions for creating a logger."""

import logging
import sys

from .args import parse_args
from .loglevel import LogLevel


def setup_logger() -> None:
    """Setup the logger to perform the required logging."""
    logger = logging.getLogger()
    stream_handler = logging.StreamHandler(sys.stderr)
    file_handler = logging.FileHandler("sportsball.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    args = parse_args()
    match args.loglevel:
        case LogLevel.DEBUG:
            stream_handler.setLevel(logging.DEBUG)
            file_handler.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        case LogLevel.INFO:
            stream_handler.setLevel(logging.INFO)
            file_handler.setLevel(logging.INFO)
            logger.setLevel(logging.INFO)
        case LogLevel.WARN:
            stream_handler.setLevel(logging.WARN)
            file_handler.setLevel(logging.WARN)
            logger.setLevel(logging.WARN)
        case LogLevel.ERROR:
            stream_handler.setLevel(logging.ERROR)
            file_handler.setLevel(logging.ERROR)
            logger.setLevel(logging.ERROR)
        case _:
            raise ValueError(f"Unrecognised loglevel: {args.loglevel}")
