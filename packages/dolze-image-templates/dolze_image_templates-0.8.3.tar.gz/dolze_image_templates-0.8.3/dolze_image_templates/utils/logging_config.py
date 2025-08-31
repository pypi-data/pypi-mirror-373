"""
Logging configuration for the Dolze Image Templates package.
"""
import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path to write logs to
    """
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Add console handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set up file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
    
    # Set default level for the root logger
    root_logger.setLevel(level)
    
    # Set level for specific loggers
    logging.getLogger('PIL').setLevel(logging.WARNING)  # Reduce PIL logging
    logging.getLogger('urllib3').setLevel(logging.WARNING)  # Reduce urllib3 logging
    logging.getLogger('fontTools').setLevel(logging.WARNING)  # Reduce fontTools logging


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name, configured with the package's logging settings.
    
    Args:
        name: Name of the logger
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
