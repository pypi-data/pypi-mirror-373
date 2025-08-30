"""
Module for configuring logging in the microservice.
"""

import logging
import os
import sys
import uuid
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Dict, Optional, Any

from mcp_proxy_adapter.config import config


class CustomFormatter(logging.Formatter):
    """
    Custom formatter for logs with colored output in console.
    """
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class RequestContextFilter(logging.Filter):
    """
    Filter for adding request context to logs.
    """
    
    def __init__(self, request_id: Optional[str] = None):
        super().__init__()
        self.request_id = request_id
    
    def filter(self, record):
        # Add request_id attribute to the record
        record.request_id = self.request_id or "no-request-id"
        return True


class RequestLogger:
    """
    Logger class for logging requests with context.
    """
    
    def __init__(self, logger_name: str, request_id: Optional[str] = None):
        """
        Initialize request logger.
        
        Args:
            logger_name: Logger name.
            request_id: Request identifier.
        """
        self.logger = logging.getLogger(logger_name)
        self.request_id = request_id or str(uuid.uuid4())
        self.filter = RequestContextFilter(self.request_id)
        self.logger.addFilter(self.filter)
    
    def debug(self, msg: str, *args, **kwargs):
        """Log message with DEBUG level."""
        self.logger.debug(f"[{self.request_id}] {msg}", *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log message with INFO level."""
        self.logger.info(f"[{self.request_id}] {msg}", *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log message with WARNING level."""
        self.logger.warning(f"[{self.request_id}] {msg}", *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log message with ERROR level."""
        self.logger.error(f"[{self.request_id}] {msg}", *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(f"[{self.request_id}] {msg}", *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log message with CRITICAL level."""
        self.logger.critical(f"[{self.request_id}] {msg}", *args, **kwargs)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    max_bytes: Optional[int] = None,
    backup_count: Optional[int] = None,
    rotation_type: Optional[str] = None,
    rotation_when: Optional[str] = None,
    rotation_interval: Optional[int] = None
) -> logging.Logger:
    """
    Configure logging for the microservice.

    Args:
        level: Logging level. By default, taken from configuration.
        log_file: Path to log file. By default, taken from configuration.
        max_bytes: Maximum log file size in bytes. By default, taken from configuration.
        backup_count: Number of rotation files. By default, taken from configuration.
        rotation_type: Type of log rotation ('size' or 'time'). By default, taken from configuration.
        rotation_when: Time unit for rotation (D, H, M, S). By default, taken from configuration.
        rotation_interval: Interval for rotation. By default, taken from configuration.

    Returns:
        Configured logger.
    """
    # Get parameters from configuration if not explicitly specified
    level = level or config.get("logging.level", "INFO")
    
    # Check debug level from config if debug is enabled
    if config.get("debug.enabled", False):
        debug_level = config.get("debug.level", "INFO")
        # Use debug level if it's more verbose than the logging level
        debug_level_num = getattr(logging, debug_level.upper(), logging.INFO)
        level_num = getattr(logging, level.upper(), logging.INFO)
        if debug_level_num < level_num:
            level = debug_level
            logger.debug(f"Using debug level from config: {debug_level}")
    
    log_file = log_file or config.get("logging.file")
    rotation_type = rotation_type or "size"  # Default to size-based rotation
    
    # Get log directory and file settings from config
    log_dir = config.get("logging.log_dir", "./logs")
    log_file_name = config.get("logging.log_file", "mcp_proxy_adapter.log")
    error_log_file = config.get("logging.error_log_file", "mcp_proxy_adapter_error.log")
    access_log_file = config.get("logging.access_log_file", "mcp_proxy_adapter_access.log")
    
    # Get rotation settings from config
    max_file_size_str = config.get("logging.max_file_size", "10MB")
    backup_count = backup_count or config.get("logging.backup_count", 5)
    
    # Parse max file size (e.g., "10MB" -> 10 * 1024 * 1024)
    max_bytes = max_bytes or _parse_file_size(max_file_size_str)
    
    # Get format settings
    log_format = config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    date_format = config.get("logging.date_format", "%Y-%m-%d %H:%M:%S")
    
    # Get output settings
    console_output = config.get("logging.console_output", True)
    file_output = config.get("logging.file_output", True)

    # Convert string logging level to constant
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    # Create root logger
    logger = logging.getLogger("mcp_proxy_adapter")
    logger.setLevel(numeric_level)
    logger.handlers = []  # Clear handlers in case of repeated call

    # Create formatter
    formatter = logging.Formatter(log_format, date_format)

    # Create console handler if enabled
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)

    # Create file handlers if file output is enabled
    if file_output and log_dir:
        # Create directory for log files if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Main log file
        if log_file_name:
            main_log_path = os.path.join(log_dir, log_file_name)
            main_handler = RotatingFileHandler(
                main_log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            main_handler.setLevel(numeric_level)
            main_handler.setFormatter(formatter)
            logger.addHandler(main_handler)

        # Error log file
        if error_log_file:
            error_log_path = os.path.join(log_dir, error_log_file)
            error_handler = RotatingFileHandler(
                error_log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            logger.addHandler(error_handler)

        # Access log file (for HTTP requests)
        if access_log_file:
            access_log_path = os.path.join(log_dir, access_log_file)
            access_handler = RotatingFileHandler(
                access_log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            access_handler.setLevel(logging.INFO)
            access_handler.setFormatter(formatter)
            logger.addHandler(access_handler)

    # Configure loggers for external libraries
    log_levels = config.get("logging.levels", {})
    for logger_name, logger_level in log_levels.items():
        lib_logger = logging.getLogger(logger_name)
        lib_logger.setLevel(getattr(logging, logger_level.upper(), logging.INFO))

    return logger


def _parse_file_size(size_str) -> int:
    """
    Parse file size string to bytes.
    
    Args:
        size_str: Size string (e.g., "10MB", "1GB", "100KB") or int
        
    Returns:
        Size in bytes
    """
    # If it's already an int, return it
    if isinstance(size_str, int):
        return size_str
    
    # Convert to string and parse
    size_str = str(size_str).upper()
    if size_str.endswith("KB"):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith("MB"):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith("GB"):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # Assume bytes if no unit specified
        return int(size_str)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name.
        
    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)


# Global logger for use throughout the application
logger = setup_logging()
