# utils/logger.py

import logging

def get_logger(name: str = __name__) -> logging.Logger:
    """
    Returns a configured logger with a console stream handler.
    For production or advanced usage, consider adding a FileHandler
    or more complex logging configurations.
    """
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers if the logger already has one
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Define the format for log messages
        formatter = logging.Formatter(
            fmt='[%(levelname)s] %(asctime)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Create a console (stream) handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

    return logger
