"""
Custom Logging Shim using Loguru 📝

Goal:
- Provide a drop-in replacement for Python's built-in 'logging' module using Loguru.
- Support:
    - logging.getLogger() interface
    - Classic logging `%` style: logger.info("Value is %s", value)
    - Environment-controlled logging level via LOGGING_LEVEL env var
    - Automatic enablement of litellm debug mode if LOGGING_LEVEL is TRACE or DEBUG
    - Efficient: avoids formatting unless necessary (log level active)

Usage:
    import myproject.logging as logging

    logger = logging.getLogger(__name__)
    logger.info("Hello %s", "world")
    logger.info("Hello {}", "world")

Environment:
    LOGGING_LEVEL=DEBUG python your_script.py
"""

import os
import sys

import litellm
from loguru import logger as loguru_logger

# --- Define log level constants ---
TRACE = "TRACE"
SUCCESS = "SUCCESS"
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"

VALID_LOG_LEVELS = {TRACE, SUCCESS, DEBUG, INFO, WARNING, ERROR, CRITICAL}

def set_level(level: str):
    """
    Dynamically sets the global log level.

    Args:
        level (str): One of TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    level = level.upper()
    if level not in VALID_LOG_LEVELS:
        warning("Invalid log level: %s", level)
        return

    loguru_logger.remove()
    loguru_logger.add(
        sink=sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
    )

    if level in {TRACE, DEBUG}:
        litellm._turn_on_debug()



# --- Setup Loguru once ---
def setup_logger():
    # Get log level from environment variable (default to WARNING)
    log_level = os.getenv("LOGGING_LEVEL", WARNING).upper()

    # Validate log level
    if log_level not in VALID_LOG_LEVELS:
        loguru_logger.warning(
            f"Invalid LOGGING_LEVEL '{log_level}' provided. Falling back to {WARNING}."
        )
        log_level = WARNING

    # Remove default logger and add new handler
    loguru_logger.remove()
    loguru_logger.add(
        sink=sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
    )

    loguru_logger.getLogger("transformers").setLevel(log_level)
    loguru_logger.getLogger("torch").setLevel(log_level)

    # Enable litellm debug if log level is TRACE or DEBUG
    if log_level in {TRACE, DEBUG}:
        litellm._turn_on_debug()


# --- Logger class that mimics logging.Logger ---
class LoggerWrapper:
    def __init__(self, name=None):
        self._logger = loguru_logger.bind(name=name or "root")

    def _log(self, level, msg, *args, **kwargs):
        # Check if level is enabled
        if args:
            try:
                msg = msg % args
            except TypeError:
                pass  # Optional: log formatting issues or just skip

        # Set correct depth so Loguru shows the actual caller
        self._logger.opt(depth=2).log(level, msg, **kwargs)


    def debug(self, msg, *args, **kwargs):
        self._log("DEBUG", msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log("INFO", msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log("WARNING", msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):  # legacy alias
        self.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log("ERROR", msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        kwargs["exc_info"] = True
        self._log("ERROR", msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log("CRITICAL", msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        if isinstance(level, str):
            level = level.upper()
        self._log(level, msg, *args, **kwargs)


# --- Module-level functions for compatibility ---
_root_logger = LoggerWrapper()


def getLogger(name=None):
    return LoggerWrapper(name)


def debug(msg, *args, **kwargs):
    _root_logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    _root_logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    _root_logger.warning(msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    _root_logger.warn(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    _root_logger.error(msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    _root_logger.exception(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    _root_logger.critical(msg, *args, **kwargs)


def basicConfig(**kwargs):
    # No-op for compatibility with standard logging
    pass
