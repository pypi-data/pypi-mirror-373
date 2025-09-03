import logging
from typing import Optional


def setup_logger(name: Optional[str] = None, silent: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR if silent else logging.INFO)

    # Remove any existing handlers (avoid duplicates if setup_logger is called multiple times)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR if silent else logging.INFO)

    # Format: [LEVEL] message
    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)

    # Attach handler to logger
    logger.addHandler(ch)
    return logger
