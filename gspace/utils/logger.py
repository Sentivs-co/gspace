import logging
import sys
from pathlib import Path


def setup_logger(
    name: str = "gspace",
    level: str | int = "INFO",
    log_file: str | Path | None = None,
    console_output: bool = True,
    format_string: str | None = None,
) -> logging.Logger:
    """
    Set up a logger for the gspace library.

    Args:
        name: Logger name
        level: Logging level (string or int)
        log_file: Optional file path for logging
        console_output: Whether to output to console
        format_string: Custom format string for logs

    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"

    formatter = logging.Formatter(format_string)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "gspace") -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set up default configuration
    if not logger.handlers:
        logger = setup_logger(name)

    return logger
