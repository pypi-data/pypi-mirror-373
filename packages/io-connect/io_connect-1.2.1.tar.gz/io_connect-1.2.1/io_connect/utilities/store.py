import sys
import logging
import asyncio
from timeit import default_timer
from typing import Optional
from datetime import datetime


class Logger:
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        message: str = "",
        log_time: bool = False,
    ):
        self.interval = 0
        self.message = message
        self.log_time = log_time
        self.logger = logger

    def __enter__(self):
        self.start = default_timer()
        return self

    def __exit__(self, *args):
        self.end = default_timer()

        if self.log_time:
            self.interval = self.end - self.start
            self.info(f"[NETWORK] {self.message} {self.interval:.4f} seconds")

    def info(self, log: str):
        if self.logger:
            self.logger.info(log)
        else:
            print(log)

    def error(self, log: str):
        if self.logger:
            self.logger.error(log)
        else:
            print(log)

    def display_log(self, log: str):
        """
        Display a log message on the console.

        This function writes a log message to the standard output stream (stdout),
        overwriting any existing content on the current line.

        Args:
            log (str): The log message to be displayed.

        Returns:
            None

        Example:
            >>> display_log("Processing...")  # Displays "Processing..." on the console

        """

        # Move the cursor to the beginning of the line
        sys.stdout.write("\r")

        # Clear the content from the cursor to the end of the line
        sys.stdout.write("\033[K")

        # Write the log message
        sys.stdout.write(log)

        # Flush the output buffer to ensure the message is displayed immediately
        sys.stdout.flush()


class AsyncLogger:
    """
    Dedicated async logger class for use in async contexts.
    Provides non-blocking logging operations using asyncio.to_thread.
    """
    
    def __init__(
        self,
        message: str = "",
    ):
        self.interval = 0
        self.message = message

    async def __aenter__(self):
        self.start = default_timer()
        return self

    async def __aexit__(self, test=None, *args):
        self.end = default_timer()
        self.interval = self.end - self.start
        await self._log("INFO",f"{test} {self.interval:.4f} seconds")

    async def _log(self, level: str, log: str):
        timestamp = datetime.now().astimezone().isoformat(timespec='seconds')
        formatted = f"[{timestamp}] | {level.upper():<8} | {log}"
        await asyncio.to_thread(print, formatted)

    async def info(self, log: str, extra_params: dict):
        """Async info logging method."""
        await self._log("INFO", log)

    async def error(self, log: str, extra_params: dict):
        """Async error logging method."""
        await self._log("ERROR", log)

    async def debug(self, log: str, extra_params: dict):
        """Async debug logging method."""
        await self._log("DEBUG", log)

    async def warning(self, log: str, extra_params: dict):
        """Async warning logging method."""
        await self._log("WARNING", log)

    async def critical(self, log: str, extra_params: dict):
        """Async error logging method."""
        await self._log("CRITICAL", log)

    async def display_log(self, log: str, extra_params: dict):
        """
        Async version of display_log for console output.
        
        Args:
            log (str): The log message to be displayed.
            
        Returns:
            None
        """
        def _display_log_sync():
            sys.stdout.write("\r")
            sys.stdout.write("\033[K")
            sys.stdout.write(log)
            sys.stdout.flush()
        
        await asyncio.to_thread(_display_log_sync)

    def timer(self, label: str = "", extra_params: dict = {}):
        return _AsyncLogTimer(self, label, extra_params)


class _AsyncLogTimer:
    """
    Internal helper for logging time with AsyncLogger.
    """

    def __init__(self, logger: AsyncLogger, label: str, extra_params: dict):
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


def ERROR_MESSAGE(response, url):
    return f"""
    [STATUS CODE] {response.status_code}
    [URL] {url}
    [SERVER INFO] {response.headers.get("Server", "Unknown Server")}
    [RESPONSE] {response.text}
    """