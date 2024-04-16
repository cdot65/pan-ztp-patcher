# utils.py

import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Configures the packages logging.

    Args: None

    Returns:
        logger: A logging object.

    Raises: None

    Example:
        logger = setup_logging()
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Configure file handler for debug level
    file_handler = RotatingFileHandler(
        "debug.log", maxBytes=5 * 1024 * 1024, backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )  # noqa E501
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Configure console handler for info level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger
