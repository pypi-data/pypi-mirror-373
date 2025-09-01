import logging
import os
import re
import sys
import tempfile
from typing import Optional

from aiko_services.main.utilities.logger import (
    _LOG_FORMAT_DATETIME,
    _LOG_FORMAT_DEFAULT,
)

__all__ = ["configure_root_logger"]


DEBUG_LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d %(levelname)-8s %(threadName)s %(name)s.%(funcName)s:%(lineno)-6d %(message)s"
)


def is_running_under_pytest():
    return "pytest" in sys.modules


def configure_root_logger(_log_path: Optional[str] = None, _log_level: Optional[str] = None):
    """Configure the root logger with file and stream handlers."""
    if _log_path is None:
        temp_file = tempfile.NamedTemporaryFile(suffix=".log", delete=False)
        _log_path = temp_file.name
        temp_file.close()
    _log_level = os.getenv("HL_LOG_LEVEL", "WARNING")

    root = logging.getLogger()
    if root.hasHandlers():
        root.handlers.clear()

    log_format = DEBUG_LOG_FORMAT if _log_level == "DEBUG" else _LOG_FORMAT_DEFAULT
    formatter = logging.Formatter(
        log_format,
        datefmt=_LOG_FORMAT_DATETIME,
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    handlers = [stream_handler]

    log_level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = log_level_mapping.get(_log_level)
    if log_level is None:
        raise SystemExit(f"Invalid log_level '{_log_level}'")

    if not is_running_under_pytest():
        # Ensure log_path exists
        directory = os.path.dirname(_log_path)
        os.makedirs(directory, exist_ok=True)

        if not os.path.exists(_log_path):
            with open(_log_path, "w") as file:
                file.write("")  # Creates an empty file

        # Setup File Handler
        file_handler = logging.FileHandler(_log_path)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    logging.basicConfig(handlers=handlers)
    # Set the log level for highlighter code
    logging.getLogger("highlighter").setLevel(log_level)
    logging.getLogger(__name__).debug(f"log_path: {_log_path}")

    for module_path, module_log_level in get_log_level_env_vars().items():
        logging.getLogger(module_path).setLevel(module_log_level)


def get_log_level_env_vars():
    """Lookup log-level directives from environment variables
    matching the pattern:
        LOG_LEVEL_module_DOT_path_DOT_segment=INFO
    into {"module.path.segment": "INFO"}
    """
    pattern = re.compile(r"^LOG_LEVEL_(.*)$")
    results = {}
    for key, value in os.environ.items():
        match = pattern.match(key)
        if match:
            # Replace all "_DOT_" with "." in the matched part
            dotted_path = match.group(1).replace("_DOT_", ".")
            results[dotted_path] = value
    return results


class ColourStr:
    HEADER = "\033[95m"

    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    ORANGE = "\033[93m"
    RED = "\033[91m"

    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    RESET = "\033[0m"

    @staticmethod
    def blue(s):
        return ColourStr.BLUE + s + ColourStr.RESET

    @staticmethod
    def cyan(s):
        return ColourStr.CYAN + s + ColourStr.RESET

    @staticmethod
    def green(s):
        return ColourStr.GREEN + s + ColourStr.RESET

    @staticmethod
    def red(s):
        return ColourStr.RED + s + ColourStr.RESET

    @staticmethod
    def bold(s):
        return ColourStr.BOLD + s + ColourStr.RESET

    @staticmethod
    def underline(s):
        return ColourStr.UNDERLINE + s + ColourStr.RESET
