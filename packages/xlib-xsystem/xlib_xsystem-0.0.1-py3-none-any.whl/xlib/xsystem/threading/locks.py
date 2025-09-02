"""
Enhanced locking utilities for thread-safe operations.
"""

import logging
import threading
import time
from contextlib import contextmanager
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EnhancedRLock:
    """
    Enhanced reentrant lock with timeout support and improved context management.
    """

    def __init__(self, timeout: Optional[float] = None, name: Optional[str] = None):
        """
        Initialize enhanced lock.

        Args:
            timeout: Default timeout in seconds for acquire operations
            name: Optional name for debugging purposes
        """
        self._lock = threading.RLock()
        self._default_timeout = timeout
        self._name = name or f"EnhancedRLock-{id(self)}"
        self._current_holders = 0  # Current recursive acquisition count
        self._total_acquisitions = 0  # Total number of acquisitions
        self._last_acquired_at: Optional[float] = None

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire the lock with optional timeout.

        Args:
            timeout: Timeout in seconds, uses default if None

        Returns:
            True if lock was acquired, False if timeout occurred
        """
        effective_timeout = timeout if timeout is not None else self._default_timeout

        start_time = time.time()
        acquired = self._lock.acquire(timeout=effective_timeout)

        if acquired:
            self._current_holders += 1
            self._total_acquisitions += 1
            self._last_acquired_at = time.time()
            acquire_time = self._last_acquired_at - start_time

            if acquire_time > 0.1:  # Log if acquisition took more than 100ms
                logger.debug(
                    f"Lock '{self._name}' acquired after {acquire_time:.3f}s "
                    f"(total: {self._total_acquisitions}, current: {self._current_holders})"
                )
        else:
            logger.warning(
                f"Failed to acquire lock '{self._name}' within "
                f"{effective_timeout}s timeout"
            )

        return acquired

    def release(self) -> None:
        """Release the lock."""
        try:
            if self._current_holders > 0:
                self._current_holders -= 1
            self._lock.release()
        except RuntimeError as e:
            logger.error(f"Error releasing lock '{self._name}': {e}")
            raise

    def locked(self) -> bool:
        """Check if the lock is currently held."""
        return self._lock.locked() if hasattr(self._lock, "locked") else False

    @contextmanager
    def timeout_context(self, timeout: float) -> None:
        """
        Context manager for lock acquisition with timeout.

        Args:
            timeout: Timeout in seconds

        Raises:
            TimeoutError: If lock cannot be acquired within timeout
        """
        if not self.acquire(timeout=timeout):
            raise TimeoutError(
                f"Could not acquire lock '{self._name}' within {timeout}s"
            )

        try:
            yield
        finally:
            self.release()

    @contextmanager
    def safe_context(self) -> None:
        """
        Safe context manager that always releases the lock.
        """
        self.acquire()
        try:
            yield
        finally:
            try:
                self.release()
            except RuntimeError:
                # Already released or not owned by current thread
                pass

    def __enter__(self) -> "EnhancedRLock":
        """Context manager entry."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.release()

    def get_stats(self) -> dict:
        """
        Get lock statistics for debugging.

        Returns:
            Dictionary with lock statistics
        """
        return {
            "name": self._name,
            "acquisition_count": self._total_acquisitions,
            "current_holders": self._current_holders,
            "is_locked": self.locked(),
            "last_acquired_at": self._last_acquired_at,
            "default_timeout": self._default_timeout,
        }
