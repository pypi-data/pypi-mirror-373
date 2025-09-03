"""Functions to help tracing the application, i.e. via logging.
"""
import logging
import threading
from typing import Callable

# If humanize package is installed, use it to format bytes
try:
    from humanize import naturalsize
except ImportError:  # TODO: It is bad-practice to catch ImportErrors... Fix TBD
    def naturalsize(num: int) -> str:
        return f'{num} Bytes'

class DownloadTracer:
    """Log meta-info about any long-running download task.

    Note: This is Thread-safe -- can be used with stdlib "`threading`" module.
        Downloads are I/O bound anyhow, so multithreading works well.
    """

    def __init__(
        self, service_name: str, threshold_bytes: int = 10000, log_function: Callable = logging.info
    ):
        self._name = service_name
        self._threshold = threshold_bytes
        self._total_bytes_downloaded = 0
        self._prior_total_bytes_downloaded = 0
        self._lock = threading.Lock()
        self._lock_timeout = 0.1
        self._log_function = log_function


    @property
    def total_bytes(self):
        return self._total_bytes_downloaded

    def trace(self, data_len: int):
        """Log message for every  data has been Add data_len to the running total."""
        if self._lock.acquire(blocking=True, timeout=1):
            try:
                self._total_bytes_downloaded += data_len
                if (
                    self._total_bytes_downloaded >   self._threshold 
                                                + self._prior_total_bytes_downloaded
                ):
                    self._prior_total_bytes_downloaded = self._total_bytes_downloaded
                    self._log_downloaded_bytes()
            finally:
                self._lock.release()
        else:
            pass
        self._asyncio_loop

    def _log_downloaded_bytes(self):
        """Log the total bytes downloaded from this service."""
        bytes_downloaded_str = f'{naturalsize(self._total_bytes_downloaded)} Bytes'
        self._log_function(
            f'Total downloaded from {self._name}: {bytes_downloaded_str}'
        )