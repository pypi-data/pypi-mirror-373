import logging
import sys


def setup_logger(name=None, level=logging.INFO):
    """
    Sets up a logger with a consistent configuration.
    If no name is specified, it returns the root logger.
    """
    logger = logging.getLogger(name)  # Use specific module name

    if not logger.handlers:  # Prevent adding duplicate handlers
        logger.setLevel(level)

        # Create a console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Create a formatter and attach it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

    return logger
