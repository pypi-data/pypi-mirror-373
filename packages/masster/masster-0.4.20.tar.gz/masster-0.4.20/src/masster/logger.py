# masster/logger.py
"""
Simple logger system for masster Study and Sample instances.
Uses basic Python logging                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                # Loguru-style colors for different log levels
                level_colors = {
                    'TRACE': '\x1b[34m',      # blue
                    'DEBUG': '\x1b[36m',      # cyan
                    'INFO': '\x1b[37m',       # white
                    'SUCCESS': '\x1b[32m',    # green
                    'WARNING': '\x1b[33m',    # yellow
                    'ERROR': '\x1b[31m',      # red
                    'CRITICAL': '\x1b[35m',   # magenta
                }

                level_str = record.levelname.ljust(8)complex loguru filtering.
"""

from __future__ import annotations
import sys
import uuid
import logging
import datetime
from typing import Any


class MassterLogger:
    """Simple logger wrapper for Study/Sample instances.
    Each instance gets its own Python logger to avoid conflicts.

    Args:
        instance_type: Type of instance ("study" or "sample")
        instance_id: Unique identifier for this instance (auto-generated if None)
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        label: Custom label to include in log messages
        sink: Output sink (defaults to sys.stdout)
    """

    def __init__(
        self,
        instance_type: str,
        instance_id: str | None = None,
        level: str = "INFO",
        label: str = "",
        sink: Any | None = None,
    ):
        if instance_id is None:
            instance_id = str(uuid.uuid4())[:8]
        self.instance_type = instance_type.lower()
        self.instance_id = instance_id
        self.level = level.upper()
        self.label = label

        # Convert string sink to actual object
        if sink == "sys.stdout" or sink is None:
            self.sink = sys.stdout
        elif isinstance(sink, str) and sink != "sys.stdout":
            # If it's a file path string, open the file for writing
            self.sink = open(sink, "a", encoding="utf-8")
        else:
            self.sink = sink

        # Create a unique logger name for this instance
        self.logger_name = f"masster.{self.instance_type}.{self.instance_id}"

        # Get a Python logger instance
        self.logger_instance = logging.getLogger(self.logger_name)

        # Remove any existing handlers to prevent duplicates
        if self.logger_instance.hasHandlers():
            self.logger_instance.handlers.clear()
        
        # Also ensure no duplicate handlers on parent loggers
        parent = self.logger_instance.parent
        while parent:
            if parent.name == "masster" and parent.hasHandlers():
                # Remove duplicate handlers from masster parent logger
                unique_handlers = []
                handler_types = set()
                for handler in parent.handlers:
                    handler_type = type(handler)
                    if handler_type not in handler_types:
                        unique_handlers.append(handler)
                        handler_types.add(handler_type)
                parent.handlers = unique_handlers
            parent = parent.parent

        self.logger_instance.setLevel(getattr(logging, self.level))

        # Create a stream handler
        self.handler = logging.StreamHandler(self.sink)

        # Create formatter that matches the original masster style
        class massterFormatter(logging.Formatter):
            def __init__(self, label):
                super().__init__()
                self.label = label

            def format(self, record):
                # Create timestamp in the same format as loguru
                dt = datetime.datetime.fromtimestamp(record.created)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Remove last 3 digits for milliseconds

                # Loguru-style colors for different log levels
                level_colors = {
                    "TRACE": "\x1b[34m",  # blue
                    "DEBUG": "\x1b[36m",  # cyan
                    "INFO": "\x1b[37m",  # white
                    "SUCCESS": "\x1b[32m",  # green
                    "WARNING": "\x1b[33m",  # yellow
                    "ERROR": "\x1b[31m",  # red
                    "CRITICAL": "\x1b[35m",  # magenta
                }

                level_str = record.levelname.ljust(8)
                level_color = level_colors.get(record.levelname, "\x1b[37m")  # default white
                label_part = self.label + " | " if self.label else ""

                # For DEBUG and TRACE levels, add module/location information
                location_info = ""
                if record.levelname in ["TRACE"]:
                    # Use caller information if available (from extra), otherwise fall back to record info
                    if hasattr(record, "caller_module"):
                        module_name = record.caller_module.split(".")[-1] if record.caller_module else "unknown"
                        line_no = record.caller_lineno
                        func_name = record.caller_funcname
                    else:
                        module_name = record.module if hasattr(record, "module") else "unknown"
                        line_no = record.lineno
                        func_name = record.funcName
                    location_info = (
                        f"\x1b[90m{module_name}:{func_name}:{line_no}\x1b[0m | "  # dim gray for location info
                    )

                # Loguru-style format: <white>timestamp</white> | <level>LEVEL</level> | <location> | <cyan>label</cyan> - <level>message</level>
                return (
                    f"\x1b[37m{timestamp}\x1b[0m | "  # white timestamp
                    f"{level_color}{level_str}\x1b[0m | "  # colored level
                    f"{location_info}"  # location info for DEBUG/TRACE
                    f"{level_color}{label_part}\x1b[0m"  # colored label
                    f"{level_color}{record.getMessage()}\x1b[0m"
                )  # colored message

        self.handler.setFormatter(massterFormatter(self.label))
        self.logger_instance.addHandler(self.handler)

        # Prevent propagation to avoid duplicate messages
        self.logger_instance.propagate = False
        
        # Additional fix: ensure no duplicate handlers in the entire logging hierarchy
        masster_logger = logging.getLogger("masster")
        if masster_logger.hasHandlers():
            # Keep only one handler per type
            unique_handlers = {}
            for handler in masster_logger.handlers:
                handler_key = (type(handler).__name__, getattr(handler, 'stream', None))
                if handler_key not in unique_handlers:
                    unique_handlers[handler_key] = handler
            masster_logger.handlers = list(unique_handlers.values())

    def update_level(self, level: str):
        """Update the logging level."""
        if level.upper() in ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]:
            self.level = level.upper()
            self.logger_instance.setLevel(getattr(logging, self.level))
        else:
            self.warning(f"Invalid logging level '{level}'. Keeping current level: {self.level}")

    def update_label(self, label: str):
        """Update the label prefix for log messages."""
        self.label = label

        # Update formatter with new label
        class massterFormatter(logging.Formatter):
            def __init__(self, label):
                super().__init__()
                self.label = label

            def format(self, record):
                dt = datetime.datetime.fromtimestamp(record.created)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                # Loguru-style colors for different log levels
                level_colors = {
                    "TRACE": "\x1b[34m",  # blue
                    "DEBUG": "\x1b[36m",  # cyan
                    "INFO": "\x1b[37m",  # white
                    "SUCCESS": "\x1b[32m",  # green
                    "WARNING": "\x1b[33m",  # yellow
                    "ERROR": "\x1b[31m",  # red
                    "CRITICAL": "\x1b[35m",  # magenta
                }

                level_str = record.levelname.ljust(8)
                level_color = level_colors.get(record.levelname, "\x1b[37m")  # default white
                label_part = self.label + " | " if self.label else ""

                # For DEBUG and TRACE levels, add module/location information
                location_info = ""
                if record.levelname in ["TRACE"]:
                    # Use caller information if available (from extra), otherwise fall back to record info
                    if hasattr(record, "caller_module"):
                        module_name = record.caller_module.split(".")[-1] if record.caller_module else "unknown"
                        line_no = record.caller_lineno
                        func_name = record.caller_funcname
                    else:
                        module_name = record.module if hasattr(record, "module") else "unknown"
                        line_no = record.lineno
                        func_name = record.funcName
                    location_info = (
                        f"\x1b[90m{module_name}:{func_name}:{line_no}\x1b[0m | "  # dim gray for location info
                    )

                # Loguru-style format: <white>timestamp</white> | <level>LEVEL</level> | <location> | <cyan>label</cyan> - <level>message</level>
                return (
                    f"\x1b[37m{timestamp}\x1b[0m | "  # white timestamp
                    f"{level_color}{level_str}\x1b[0m | "  # colored level
                    f"{location_info}"  # location info for DEBUG/TRACE
                    f"{level_color}{label_part}\x1b[0m"  # colored label
                    f"{level_color}{record.getMessage()}\x1b[0m"
                )  # colored message

        self.handler.setFormatter(massterFormatter(self.label))

    def update_sink(self, sink: Any):
        """Update the output sink for log messages."""
        # Convert string sink to actual object
        if sink == "sys.stdout":
            self.sink = sys.stdout
        else:
            self.sink = sink

        # Remove old handler and create new one with new sink
        self.logger_instance.removeHandler(self.handler)
        self.handler = logging.StreamHandler(self.sink)

        # Apply formatter
        class massterFormatter(logging.Formatter):
            def __init__(self, label):
                super().__init__()
                self.label = label

            def format(self, record):
                dt = datetime.datetime.fromtimestamp(record.created)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                # Loguru-style colors for different log levels
                level_colors = {
                    "TRACE": "\x1b[34m",  # blue
                    "DEBUG": "\x1b[36m",  # cyan
                    "INFO": "\x1b[37m",  # white
                    "SUCCESS": "\x1b[32m",  # green
                    "WARNING": "\x1b[33m",  # yellow
                    "ERROR": "\x1b[31m",  # red
                    "CRITICAL": "\x1b[35m",  # magenta
                }

                level_str = record.levelname.ljust(8)
                level_color = level_colors.get(record.levelname, "\x1b[37m")  # default white
                label_part = self.label + " | " if self.label else ""

                # For DEBUG and TRACE levels, add module/location information
                location_info = ""
                if record.levelname in ["TRACE"]:
                    # Use caller information if available (from extra), otherwise fall back to record info
                    if hasattr(record, "caller_module"):
                        module_name = record.caller_module.split(".")[-1] if record.caller_module else "unknown"
                        line_no = record.caller_lineno
                        func_name = record.caller_funcname
                    else:
                        module_name = record.module
                        line_no = record.lineno
                        func_name = record.funcName
                    location_info = (
                        f"\x1b[90m{module_name}:{func_name}:{line_no}\x1b[0m | "  # dim gray for location info
                    )

                # Loguru-style format: <white>timestamp</white> | <level>LEVEL</level> | <location> | <cyan>label</cyan> - <level>message</level>
                return (
                    f"\x1b[37m{timestamp}\x1b[0m | "  # white timestamp
                    f"{level_color}{level_str}\x1b[0m | "  # colored level
                    f"{location_info}"  # location info for DEBUG/TRACE
                    f"{level_color}{label_part}\x1b[0m"  # colored label
                    f"{level_color}{record.getMessage()}\x1b[0m"
                )  # colored message

        self.handler.setFormatter(massterFormatter(self.label))
        self.logger_instance.addHandler(self.handler)

    # Logger method delegates
    def trace(self, message: str, *args, **kwargs):
        """Log a TRACE level message (mapped to DEBUG)."""
        # Get caller frame information (skip this method and go to actual caller)
        import inspect

        frame = inspect.currentframe().f_back

        # Add caller information as extra parameters
        extra = kwargs.get("extra", {})
        extra.update({
            "caller_module": frame.f_globals.get("__name__", "unknown"),
            "caller_filename": frame.f_code.co_filename,
            "caller_lineno": frame.f_lineno,
            "caller_funcname": frame.f_code.co_name,
        })
        kwargs["extra"] = extra

        self.logger_instance.debug(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        """Log a DEBUG level message."""
        # Get caller frame information (skip this method and go to actual caller)
        import inspect

        frame = inspect.currentframe().f_back

        # Add caller information as extra parameters
        extra = kwargs.get("extra", {})
        extra.update({
            "caller_module": frame.f_globals.get("__name__", "unknown"),
            "caller_filename": frame.f_code.co_filename,
            "caller_lineno": frame.f_lineno,
            "caller_funcname": frame.f_code.co_name,
        })
        kwargs["extra"] = extra

        self.logger_instance.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log an INFO level message."""
        self.logger_instance.info(message, *args, **kwargs)

    def success(self, message: str, *args, **kwargs):
        """Log a SUCCESS level message (mapped to INFO)."""
        self.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log a WARNING level message."""
        self.logger_instance.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log an ERROR level message."""
        self.logger_instance.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log a CRITICAL level message."""
        self.logger_instance.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """Log an exception with ERROR level."""
        self.logger_instance.exception(message, *args, **kwargs)

    def remove(self):
        """Remove this logger's handler."""
        if self.handler:
            self.logger_instance.removeHandler(self.handler)
            # Close the file handle if it's not stdout
            if hasattr(self.sink, 'close') and self.sink != sys.stdout:
                try:
                    self.sink.close()
                except Exception:
                    pass  # Ignore close errors
            self.handler = None

    def __del__(self):
        """Cleanup when the logger is destroyed."""
        try:
            self.remove()
        except Exception:
            pass  # Ignore cleanup errors during destruction

    def __repr__(self):
        return f"MassterLogger(type={self.instance_type}, id={self.instance_id}, level={self.level})"
