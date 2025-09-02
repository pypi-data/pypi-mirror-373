"""
Error Recovery and Resilience Mechanisms for xSystem Library.

This module provides comprehensive error recovery, circuit breaker patterns,
retry mechanisms, and graceful degradation for production deployment.
"""

import functools
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.error_recovery")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0  # seconds
    expected_exception: Type[Exception] = Exception
    monitor_interval: float = 10.0  # seconds


@dataclass
class ErrorContext:
    """Context information for error tracking."""

    error_type: str
    error_message: str
    operation_name: str
    timestamp: float
    retry_count: int = 0
    circuit_state: str = "unknown"
    additional_info: Dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by temporarily stopping requests
    when a service is failing repeatedly.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig):
        """Initialize circuit breaker."""
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = time.time()

        # Thread safety
        self._lock = threading.RLock()

        logger.info(f"🔌 Circuit breaker '{name}' initialized")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if not self._can_execute():
            raise Exception(f"Circuit breaker '{self.name}' is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise

    def _can_execute(self) -> bool:
        """Check if execution is allowed."""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"🔄 Circuit breaker '{self.name}' moved to HALF_OPEN")
                    return True
                return False

            # HALF_OPEN state - allow one test request
            return True

    def _on_success(self) -> None:
        """Handle successful execution."""
        with self._lock:
            self.failure_count = 0
            self.last_success_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info(f"✅ Circuit breaker '{self.name}' closed (recovered)")

    def _on_failure(self) -> None:
        """Handle failed execution."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                # Test request failed, back to open
                self.state = CircuitState.OPEN
                logger.warning(f"❌ Circuit breaker '{self.name}' opened (test failed)")
            elif (
                self.state == CircuitState.CLOSED
                and self.failure_count >= self.config.failure_threshold
            ):
                # Threshold reached, open circuit
                self.state = CircuitState.OPEN
                logger.warning(
                    f"❌ Circuit breaker '{self.name}' opened (threshold reached)"
                )

    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            return self.state

    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info(f"🔄 Circuit breaker '{self.name}' reset")


class ErrorRecoveryManager:
    """
    Comprehensive error recovery and resilience manager.

    Features:
    - Multiple circuit breakers
    - Retry mechanisms with exponential backoff
    - Graceful degradation
    - Error context tracking
    - Default recovery strategies
    """

    def __init__(self) -> None:
        """Initialize error recovery manager."""
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_contexts: List[ErrorContext] = []
        self.retry_configs: Dict[str, Dict[str, Any]] = {}
        self.degradation_strategies: Dict[str, Callable] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Setup default recovery strategies
        self._setup_default_strategies()

        logger.info("🛡️ Error recovery manager initialized")

    def _setup_default_strategies(self) -> None:
        """Setup default recovery strategies for common error types."""
        # Memory errors
        self.degradation_strategies["memory"] = self._handle_memory_error

        # Timeout errors
        self.degradation_strategies["timeout"] = self._handle_timeout_error

        # Connection errors
        self.degradation_strategies["connection"] = self._handle_connection_error

        # Validation errors
        self.degradation_strategies["validation"] = self._handle_validation_error

    def _handle_memory_error(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Handle memory-related errors."""
        logger.warning("🧠 Memory error detected, attempting cleanup")

        # Force garbage collection
        import gc

        collected = gc.collect()

        # Try to reduce memory usage
        if "memory_monitor" in context:
            context["memory_monitor"].force_cleanup()

        logger.info(f"🧹 Memory cleanup completed: {collected} objects collected")
        return None

    def _handle_timeout_error(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Handle timeout errors."""
        logger.warning("⏰ Timeout error detected, using cached result if available")

        # Return cached result if available
        if "cache" in context and context["cache"]:
            return context["cache"].get("last_result")

        return None

    def _handle_connection_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> Any:
        """Handle connection errors."""
        logger.warning("🔌 Connection error detected, using fallback")

        # Use fallback data if available
        if "fallback_data" in context:
            return context["fallback_data"]

        return None

    def _handle_validation_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> Any:
        """Handle validation errors."""
        logger.warning("✅ Validation error detected, using default values")

        # Return default values if available
        if "default_values" in context:
            return context["default_values"]

        return None

    def add_circuit_breaker(self, name: str, config: CircuitBreakerConfig) -> None:
        """Add a circuit breaker."""
        with self._lock:
            self.circuit_breakers[name] = CircuitBreaker(name, config)
            logger.info(f"🔌 Added circuit breaker: {name}")

    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name."""
        with self._lock:
            return self.circuit_breakers.get(name)

    def retry_with_backoff(
        self,
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,),
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute function with exponential backoff retry.

        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            backoff_factor: Factor to multiply delay by on each retry
            exceptions: Tuple of exceptions to retry on
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None
        delay = base_delay

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e

                if attempt == max_retries:
                    # Final attempt failed
                    logger.error(f"❌ Function failed after {max_retries} retries: {e}")
                    raise

                # Log retry attempt
                logger.warning(
                    f"🔄 Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {e}"
                )

                # Wait before retry
                time.sleep(delay)

                # Calculate next delay
                delay = min(delay * backoff_factor, max_delay)

        # This should never be reached
        raise last_exception

    def graceful_degradation(
        self,
        primary_func: Callable,
        fallback_func: Callable,
        error_types: tuple = (Exception,),
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute primary function with graceful degradation to fallback.

        Args:
            primary_func: Primary function to try first
            fallback_func: Fallback function if primary fails
            error_types: Types of errors that trigger fallback
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Result from primary or fallback function
        """
        try:
            return primary_func(*args, **kwargs)
        except error_types as e:
            logger.warning(f"⚠️ Primary function failed, using fallback: {e}")

            # Record error context
            self._record_error_context(
                e,
                "graceful_degradation",
                {
                    "primary_func": primary_func.__name__,
                    "fallback_func": fallback_func.__name__,
                },
            )

            try:
                return fallback_func(*args, **kwargs)
            except Exception as fallback_error:
                logger.error(
                    f"❌ Both primary and fallback functions failed: {fallback_error}"
                )
                raise fallback_error

    def handle_error(
        self, error: Exception, operation_name: str, context: Dict[str, Any] = None
    ) -> Any:
        """
        Handle error using appropriate recovery strategy.

        Args:
            error: The error that occurred
            operation_name: Name of the operation that failed
            context: Additional context information

        Returns:
            Result from recovery strategy or None
        """
        if context is None:
            context = {}

        # Record error context
        self._record_error_context(error, operation_name, context)

        # Determine error type
        error_type = self._classify_error(error)

        # Get appropriate strategy
        strategy = self.degradation_strategies.get(error_type)
        if strategy:
            try:
                return strategy(error, context)
            except Exception as strategy_error:
                logger.error(f"❌ Recovery strategy failed: {strategy_error}")

        # No strategy available
        logger.error(f"❌ No recovery strategy for error type: {error_type}")
        return None

    def _classify_error(self, error: Exception) -> str:
        """Classify error type for strategy selection."""
        error_name = type(error).__name__.lower()

        if "memory" in error_name or "MemoryError" in str(type(error)):
            return "memory"
        elif "timeout" in error_name or "TimeoutError" in str(type(error)):
            return "timeout"
        elif "connection" in error_name or "ConnectionError" in str(type(error)):
            return "connection"
        elif "validation" in error_name or "ValueError" in str(type(error)):
            return "validation"
        else:
            return "unknown"

    def _record_error_context(
        self, error: Exception, operation_name: str, context: Dict[str, Any]
    ) -> None:
        """Record error context for analysis."""
        error_context = ErrorContext(
            error_type=type(error).__name__,
            error_message=str(error),
            operation_name=operation_name,
            timestamp=time.time(),
            additional_info=context,
        )

        with self._lock:
            self.error_contexts.append(error_context)

            # Keep only recent errors (last 100)
            if len(self.error_contexts) > 100:
                self.error_contexts = self.error_contexts[-100:]

    def get_error_contexts(self) -> List[ErrorContext]:
        """Get all recorded error contexts."""
        with self._lock:
            return self.error_contexts.copy()

    def get_circuit_breaker_states(self) -> Dict[str, str]:
        """Get states of all circuit breakers."""
        with self._lock:
            return {
                name: cb.get_state().value for name, cb in self.circuit_breakers.items()
            }

    def reset_all_circuit_breakers(self) -> None:
        """Reset all circuit breakers."""
        with self._lock:
            for cb in self.circuit_breakers.values():
                cb.reset()
            logger.info("🔄 All circuit breakers reset")


# Global instance for easy access
_error_recovery_manager: Optional[ErrorRecoveryManager] = None


def get_error_recovery_manager() -> ErrorRecoveryManager:
    """Get the global error recovery manager instance."""
    global _error_recovery_manager
    if _error_recovery_manager is None:
        _error_recovery_manager = ErrorRecoveryManager()
    return _error_recovery_manager


def circuit_breaker(name: str, config: CircuitBreakerConfig = None):
    """
    Decorator for circuit breaker pattern.

    Args:
        name: Circuit breaker name
        config: Circuit breaker configuration
    """
    if config is None:
        config = CircuitBreakerConfig()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            manager = get_error_recovery_manager()

            # Get or create circuit breaker
            cb = manager.get_circuit_breaker(name)
            if cb is None:
                manager.add_circuit_breaker(name, config)
                cb = manager.get_circuit_breaker(name)

            return cb.call(func, *args, **kwargs)

        return wrapper

    return decorator


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Factor to multiply delay by on each retry
        exceptions: Tuple of exceptions to retry on
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            manager = get_error_recovery_manager()
            return manager.retry_with_backoff(
                func,
                max_retries,
                base_delay,
                max_delay,
                backoff_factor,
                exceptions,
                *args,
                **kwargs,
            )

        return wrapper

    return decorator


def graceful_degradation(
    primary_func: Callable, fallback_func: Callable, error_types: tuple = (Exception,)
):
    """
    Decorator for graceful degradation pattern.

    Args:
        primary_func: Primary function to try first
        fallback_func: Fallback function if primary fails
        error_types: Types of errors that trigger fallback
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            manager = get_error_recovery_manager()
            return manager.graceful_degradation(
                primary_func, fallback_func, error_types, *args, **kwargs
            )

        return wrapper

    return decorator


def handle_error(operation_name: str, context: Dict[str, Any] = None):
    """
    Decorator for error handling with recovery strategies.

    Args:
        operation_name: Name of the operation
        context: Additional context information
    """
    if context is None:
        context = {}

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                manager = get_error_recovery_manager()
                return manager.handle_error(e, operation_name, context)

        return wrapper

    return decorator
