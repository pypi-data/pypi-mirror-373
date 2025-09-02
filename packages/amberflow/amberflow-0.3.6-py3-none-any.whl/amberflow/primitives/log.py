import logging
import warnings
from pathlib import Path

from .. import __version__, __logging_name__

__all__ = ("get_null_logger", "set_logger")


def get_null_logger() -> logging.Logger:
    """
    Get a logger instance that won't output anything, unless the user has previously created a logger with the same
    name. Thus, if the user doesn't want to see any output, they can just not create a logger.

    Returns:
        logging.Logger: A logger instance with INFO level and a NullHandler.
    """
    logger = logging.getLogger(__logging_name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.NullHandler())
    return logger


def set_logger(logfile: Path, logging_level=logging.INFO, filemode: str = "a") -> logging.Logger:
    """
    Set up a logger that logs messages to both a file and the console.

    Args:
       logfile (Path): The path to the log file.
       logging_level (int): The logging level (default is logging.INFO).
       filemode (str): The mode to open the log file (default is "a" for append).

    Returns:
       logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(f"{__logging_name__}")
    logger.setLevel(logging_level)

    if len(logger.handlers) != 0:
        # keep the existing handlers if they are already set up
        return logger

    formatter = logging.Formatter(
        "{asctime} - {levelname} - {version} {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        defaults={"version": __version__},
    )

    # logger to console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # logger to file
    if Path(logfile).parent.is_dir():
        file_handler = logging.FileHandler(filename=logfile, mode=filemode)
        file_handler.setLevel(logging_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        warnings.warn(f"{logfile.parent} doesn't exist. Cannot create logfile.")

    return logger
