"""
Generic type safety validation.

This module provides type validation utilities for safe operations
with untrusted data in any application.
"""

from typing import Any


class GenericSecurityError(Exception):
    """Base exception for generic security-related errors."""

    pass


class SafeTypeValidator:
    """Validates types for safe operations."""

    # Allowed types for untrusted data
    SAFE_TYPES = (str, int, float, bool, list, dict, type(None))

    # Types that are always safe to cache
    IMMUTABLE_TYPES = (str, int, float, bool, tuple, frozenset, type(None))

    @classmethod
    def is_safe_type(cls, value: Any) -> bool:
        """Check if a value is of a safe type."""
        return isinstance(value, cls.SAFE_TYPES)

    @classmethod
    def is_immutable_type(cls, value: Any) -> bool:
        """Check if a value is of an immutable type."""
        return isinstance(value, cls.IMMUTABLE_TYPES)

    @classmethod
    def validate_untrusted_data(cls, data: Any, max_depth: int = 100) -> None:
        """
        Validate data from untrusted sources.

        Args:
            data: Data to validate
            max_depth: Maximum recursion depth to prevent deep recursion attacks

        Raises:
            GenericSecurityError: If data contains unsafe types
        """

        def _check_recursive(obj: Any, depth: int = 0) -> None:
            if depth > max_depth:
                raise GenericSecurityError("Data structure too deep")

            if not cls.is_safe_type(obj):
                raise GenericSecurityError(f"Unsafe type detected: {type(obj)}")

            if isinstance(obj, dict):
                for key, value in obj.items():
                    if not isinstance(key, str):
                        raise GenericSecurityError(
                            f"Non-string key detected: {type(key)}"
                        )
                    _check_recursive(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    _check_recursive(item, depth + 1)

        _check_recursive(data)

    @classmethod
    def sanitize_for_caching(cls, data: Any) -> Any:
        """
        Sanitize data for safe caching by ensuring immutable types.

        Args:
            data: Data to sanitize

        Returns:
            Sanitized data safe for caching
        """
        if cls.is_immutable_type(data):
            return data
        elif isinstance(data, list):
            return tuple(cls.sanitize_for_caching(item) for item in data)
        elif isinstance(data, dict):
            return tuple(
                sorted(
                    (key, cls.sanitize_for_caching(value))
                    for key, value in data.items()
                )
            )
        else:
            # For non-safe types, return a safe representation
            return str(data)


def validate_untrusted_data(data: Any, max_depth: int = 100) -> None:
    """Convenience function for validating untrusted data."""
    SafeTypeValidator.validate_untrusted_data(data, max_depth)


def is_safe_type(value: Any) -> bool:
    """Convenience function for checking safe types."""
    return SafeTypeValidator.is_safe_type(value)


def is_immutable_type(value: Any) -> bool:
    """Convenience function for checking immutable types."""
    return SafeTypeValidator.is_immutable_type(value)
