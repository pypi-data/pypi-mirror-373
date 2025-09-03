import asyncio
import glob
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from timeit import default_timer
from typing import Optional

import aiofiles
from typeguard import typechecked

import io_connect.constants as c


@typechecked
class AsyncLoggerConfigurator:
    __version__ = c.VERSION
    """
    An async version of the LoggerConfigurator class for configuring and setting up logging for a service.
    It supports both console and file logging with structured JSON format, with async file operations and rotation.

    Attributes:
        service_name (str): The name of the service used in the log entries.
        log_dir (str): The directory where the log files will be saved. Defaults to './logs' in the application root.
        log_level (int): The logging level (e.g., DEBUG, INFO). Defaults to logging.DEBUG. logging.DEBUG has a value of 10. logging.INFO has a value of 20. logging.WARNING has a value of 30. logging.ERROR has a value of 40. logging.CRITICAL has a value of 50.
        rotation_period (str, optional): Time interval for rotation. Defaults to 'M' (minutes). Options "S": Seconds,"M": Minutes,"H": Hours,"D": Days
        rotation_interval (int, optional): How often to rotate logs based on `when`. Defaults to 5.
        rotation_backup_count (int, optional): Number of old logs to keep. Defaults to 10.
        message_format(boolean, optional)=Determines if the console log message should be formatted in JSON. Defaults to False.
        console_logger(boolean, optional)=Determines if we should log console log message should be formatted in JSON. Defaults to True.
    Methods:
        get_logger():
            Returns the configured logger instance.
        async_log(level, message, extra=None):
            Async method for logging messages with optional extra data.
    Example:
        # Initializing Async Logger
        logger_config = AsyncLoggerConfigurator(
            service_name="MyService", 
            log_dir="./custom_logs", 
            log_level=logging.INFO, 
            rotation_when="H", 
            rotation_interval=1, 
            rotation_backup_count=5
        )
        logger = logger_config.get_logger()
        
        # Async logging
        await logger_config.async_log("info", "User login successful", {"user": "admin", "action": "login", "ip": "192.168.1.1"})
        await logger_config.async_log("error", "Error while processing request", {"error_code": 500, "request_id": "abc123"})
    """

    def __init__(
        self,
        service_name: str,
        log_dir: str = "logs",
        log_level: int = logging.DEBUG,
        rotation_period: str = "M",
        rotation_interval: int = 5,
        rotation_backup_count: int = 10,
        format_message: bool = False,
        console_logger: bool = True,
    ):
        """
        Initializes the AsyncLoggerConfigurator class to set up async logging for the service.

        Args:
            service_name (str): The name of the service (used in the logs).
            log_dir (str, optional): Directory where logs are stored (defaults to './logs').
            log_level (int, optional): The logging level (e.g., logging.DEBUG). Default is logging.DEBUG.
            rotation_period (str, optional): Time interval for rotation. Defaults to 'M' (minutes).Options "S": Seconds,"M": Minutes,"H": Hours,"D": Days
            rotation_interval (int, optional): How often to rotate logs based on `when`. Defaults to 5.
            rotation_backup_count (int, optional): Number of old logs to keep. Defaults to 10.
            format_message(boolean, optional)=Determines if the console log message should be formatted in JSON. Defaults to True.
        """
        self.service_name = service_name
        # Default to "logs" directory in the application's root if log_dir is not specified
        self.log_dir = log_dir or os.path.join(
            os.path.dirname(os.path.abspath(sys.argv[0])), "logs"
        )
        self.log_level = log_level
        self.rotation_when = rotation_period
        self.rotation_interval = rotation_interval
        self.rotation_backup_count = rotation_backup_count
        self.message_format = format_message
        self.console_logger = console_logger
        self.logger = self._initialize_logger()
        self.log_queue = asyncio.Queue()
        self._log_task = None

        # File rotation state
        self.current_log_file = None
        self.file_creation_time = None
        self._rotation_lock = asyncio.Lock()

    class AsyncDynamicJSONFormatter(logging.Formatter):
        """
        Custom async formatter to output logs in a structured JSON format.

        This formatter includes the following fields in each log entry:
            - timestamp: The time when the log was generated.
            - service: The name of the service generating the log.
            - level: The log level (e.g., DEBUG, INFO).
            - message: The log message.

        It also includes any additional information passed via the `extra` field or other log attributes.

        Methods:
            format(record):
                Converts the log record into a structured JSON object.
        """

        def __init__(self, service_name):
            super().__init__()
            self.service_name = service_name

        def format(self, record):
            """
            Formats the log record into a structured JSON object.

            Args:
                record (logging.LogRecord): The log record to format.

            Returns:
                str: A JSON string representation of the log record.
            """
            # Base log structure
            log_record = {
                "timestamp": self.formatTime(record),
                "service": self.service_name,
                "level": record.levelname,
                "message": record.getMessage(),
            }

            # Dynamically include extra attributes
            if hasattr(record, "extra") and isinstance(record.extra, dict):
                log_record.update(record.extra)
            else:
                # Include attributes directly from the record dict
                for key, value in record.__dict__.items():
                    if key not in [
                        "args",
                        "msg",
                        "levelname",
                        "levelno",
                        "pathname",
                        "filename",
                        "module",
                        "exc_info",
                        "exc_text",
                        "stack_info",
                        "lineno",
                        "funcName",
                        "created",
                        "msecs",
                        "relativeCreated",
                        "thread",
                        "threadName",
                        "processName",
                        "process",
                        "name",
                    ] and not key.startswith("_"):
                        log_record[key] = value

            return json.dumps(log_record)

    def _configure_handler(self, handler, formatter):
        """
        Configures the log handler with the specified formatter and log level.

        Args:
            handler (logging.Handler): The logging handler to configure (e.g., StreamHandler, TimedRotatingFileHandler).
            formatter (logging.Formatter): The formatter to apply to the handler.

        Returns:
            logging.Handler: The configured logging handler.
        """
        handler.setLevel(self.log_level)
        handler.setFormatter(formatter)
        return handler

    async def _ensure_log_dir_exists(self):
        """
        Async method to ensure log directory exists.
        """
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    def _get_rotation_interval_seconds(self):
        """
        Convert rotation period and interval to seconds.
        """
        multipliers = {
            "S": 1,  # seconds
            "M": 60,  # minutes
            "H": 3600,  # hours
            "D": 86400,  # days
        }
        return self.rotation_interval * multipliers.get(self.rotation_when, 60)

    def _get_log_file_path(self, timestamp=None):
        """
        Get the current log file path.
        """
        base_name = f"{self.service_name}_logs.log"
        return os.path.join(self.log_dir, base_name)

    def _get_rotated_file_path(self, timestamp):
        """
        Get the path for a rotated log file with timestamp.
        """
        timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        rotated_name = f"{self.service_name}_logs.log.{timestamp_str}"
        return os.path.join(self.log_dir, rotated_name)

    async def _should_rotate(self):
        """
        Check if the log file should be rotated based on time.
        """
        if self.file_creation_time is None:
            return False

        current_time = datetime.now()
        rotation_interval_seconds = self._get_rotation_interval_seconds()

        time_since_creation = (current_time - self.file_creation_time).total_seconds()
        return time_since_creation >= rotation_interval_seconds

    async def _rotate_log_file(self):
        """
        Rotate the current log file.
        """
        async with self._rotation_lock:
            if self.current_log_file and os.path.exists(self.current_log_file):
                # Create rotated filename with timestamp
                rotation_time = self.file_creation_time or datetime.now()
                rotated_path = self._get_rotated_file_path(rotation_time)

                try:
                    # Move current log file to rotated name
                    os.rename(self.current_log_file, rotated_path)
                    print(
                        f"Rotated log file: {self.current_log_file} -> {rotated_path}"
                    )

                    # Clean up old log files
                    await self._cleanup_old_logs()

                except Exception as e:
                    print(f"Error rotating log file: {e}")

            # Reset file creation time for new file
            self.file_creation_time = datetime.now()

    async def _cleanup_old_logs(self):
        """
        Remove old rotated log files beyond the backup count.
        """
        try:
            # Find all rotated log files
            pattern = os.path.join(self.log_dir, f"{self.service_name}_logs.log.*")
            rotated_files = glob.glob(pattern)

            # Sort by modification time (newest first)
            rotated_files.sort(key=os.path.getmtime, reverse=True)

            # Remove files beyond backup count
            files_to_remove = rotated_files[self.rotation_backup_count :]
            for old_file in files_to_remove:
                try:
                    os.remove(old_file)
                    print(f"Removed old log file: {old_file}")
                except Exception as e:
                    print(f"Error removing old log file {old_file}: {e}")

        except Exception as e:
            print(f"Error during log cleanup: {e}")

    def _initialize_logger(self):
        """
        Initializes the logger with both console and file handlers. The console handler
        will output logs to stdout, and the file handler will save logs to a file with
        rotation (creating new files after a set interval).

        Returns:
            logging.Logger: The configured logger instance.
        """
        logger = logging.getLogger(f"async_{self.service_name}")
        logger.setLevel(self.log_level)

        # Clear any existing handlers to avoid duplicates
        logger.handlers.clear()

        # Formatter for structured JSON logs
        formatter = self.AsyncDynamicJSONFormatter(self.service_name)

        if self.console_logger:
            # Configure console handler
            console_handler = logging.StreamHandler(sys.stdout)
            if self.message_format:
                # If message_format is True, apply JSON format
                console_handler.setFormatter(formatter)
            else:
                # If message_format is False, use a simple log message format (plain text)
                console_handler.setFormatter(logging.Formatter("%(message)s"))

            logger.addHandler(console_handler)

        # Note: File handler will be configured async when needed
        return logger

    async def _async_file_logger_task(self):
        """
        Async task that processes log entries from the queue and writes them to file.
        """
        await self._ensure_log_dir_exists()

        self.current_log_file = self._get_log_file_path()
        self.file_creation_time = datetime.now()

        while True:
            try:
                # Wait for log entry
                log_entry = await self.log_queue.get()

                if log_entry is None:  # Shutdown signal
                    break

                # Check if rotation is needed
                if await self._should_rotate():
                    await self._rotate_log_file()

                # Write to file asynchronously
                async with aiofiles.open(
                    self.current_log_file, mode="a", encoding="utf-8"
                ) as f:
                    await f.write(log_entry + "\n")
                    await f.flush()

                self.log_queue.task_done()

            except Exception as e:
                print(f"Error in async file logger: {e}")

    async def start_async_logging(self):
        """
        Starts the async logging task.
        """
        if self._log_task is None or self._log_task.done():
            self._log_task = asyncio.create_task(self._async_file_logger_task())

    async def stop_async_logging(self):
        """
        Stops the async logging task gracefully.
        """
        if self._log_task and not self._log_task.done():
            await self.log_queue.put(None)  # Send shutdown signal
            await self._log_task
            self._log_task = None

    async def async_log(self, level: str, message: str, extra: Optional[dict] = None):
        """
        Async method for logging messages.

        Args:
            level (str): Log level ('debug', 'info', 'warning', 'error', 'critical')
            message (str): The log message
            extra (dict, optional): Additional data to include in the log
        """
        # Ensure async logging task is running
        await self.start_async_logging()

        # Create log record
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "level": level.upper(),
            "message": message,
        }

        if extra:
            log_record.update(extra)

        log_entry = json.dumps(log_record)

        # Add to queue for async file writing
        await self.log_queue.put(log_entry)

        # Also log to console if enabled
        if self.console_logger:
            if self.message_format:
                print(log_entry)
            else:
                print(message)

    def get_logger(self):
        """
        Retrieves the configured logger instance.

        Returns:
            logging.Logger: The logger instance configured with console handler.
        """
        return self.logger

    async def __aenter__(self):
        """
        Async context manager entry.
        """
        await self.start_async_logging()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit.
        """
        await self.stop_async_logging()

    async def force_rotation(self):
        """
        Force a log rotation manually (useful for testing).
        """
        await self._rotate_log_file()

    # AsyncDataAccess compatibility methods
    async def info(self, message: str, extra_params: Optional[dict] = None):
        """
        Async info logging method compatible with AsyncDataAccess interface.

        Args:
            message (str): The log message
            extra_params (dict, optional): Additional parameters for logging context
        """
        await self.async_log("info", message, extra_params)

    async def error(self, message: str, extra_params: Optional[dict] = None):
        """
        Async error logging method compatible with AsyncDataAccess interface.

        Args:
            message (str): The log message
            extra_params (dict, optional): Additional parameters for logging context
        """
        await self.async_log("error", message, extra_params)

    async def debug(self, message: str, extra_params: Optional[dict] = None):
        """
        Async debug logging method compatible with AsyncDataAccess interface.

        Args:
            message (str): The log message
            extra_params (dict, optional): Additional parameters for logging context
        """
        await self.async_log("debug", message, extra_params)

    async def warning(self, message: str, extra_params: Optional[dict] = None):
        """
        Async warning logging method compatible with AsyncDataAccess interface.

        Args:
            message (str): The log message
            extra_params (dict, optional): Additional parameters for logging context
        """
        await self.async_log("warning", message, extra_params)

    async def critical(self, message: str, extra_params: Optional[dict] = None):
        """
        Async critical logging method compatible with AsyncDataAccess interface.

        Args:
            message (str): The log message
            extra_params (dict, optional): Additional parameters for logging context
        """
        await self.async_log("critical", message, extra_params)

    def timer(self, label: str = "", extra_params: dict = {}):
        return _AsyncLogTimer(self, label, extra_params)


class _AsyncLogTimer:
    """
    Internal helper for logging time with AsyncLogger.
    """

    def __init__(
        self,
        logger: AsyncLoggerConfigurator,
        label: str,
        extra_params: dict,
    ):
        self.logger = logger
        self.label = label
        self.extra_params = extra_params

    async def __aenter__(self):
        self.start = default_timer()
        return self

    async def __aexit__(self, *args):
        self.end = default_timer()
        elapsed = self.end - self.start
        msg = f"{self.label} {elapsed:.4f} seconds"
        await self.logger.info(msg, self.extra_params)
