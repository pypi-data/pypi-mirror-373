"""
Thread-safe factory pattern for handler registration and management.
"""

import logging
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ThreadSafeFactory(Generic[T]):
    """
    Generic thread-safe factory for handler registration and retrieval.

    This can be used as a base class for any handler factory that needs
    thread-safe registration and lookup of handlers by name/extension.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, Type[T]] = {}
        self._extensions: Dict[str, str] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._methods_generated = False
        self._methods_lock = threading.Lock()

    def register(
        self, name: str, handler_class: Type[T], extensions: Optional[List[str]] = None
    ) -> None:
        """
        Register a handler with optional file extensions.

        Args:
            name: Handler name (case-insensitive)
            handler_class: Handler class to register
            extensions: Optional list of file extensions this handler supports
        """
        with self._lock:
            name_lower = name.lower()
            self._handlers[name_lower] = handler_class

            processed_exts: List[str] = []
            if extensions:
                processed_exts = [ext.lower().lstrip(".") for ext in extensions]
            elif name_lower not in processed_exts:
                processed_exts.append(name_lower)

            for ext in processed_exts:
                if ext in self._extensions and self._extensions[ext] != name_lower:
                    logger.debug(
                        f"Extension '.{ext}' registered for both "
                        f"'{self._extensions[ext]}' and '{name_lower}'. "
                        "Will use content detection to choose."
                    )
                self._extensions[ext] = name_lower

    def get_handler(self, name: str) -> Type[T]:
        """
        Get a handler by name.

        Args:
            name: Handler name (case-insensitive)

        Returns:
            Handler class

        Raises:
            KeyError: If handler not found
        """
        with self._lock:
            handler = self._handlers.get(name.lower())
            if not handler:
                raise KeyError(f"No handler registered for: {name}")
            return handler

    def get_handler_if_exists(self, name: str) -> Optional[Type[T]]:
        """
        Get a handler by name, returning None if not found.

        Args:
            name: Handler name (case-insensitive)

        Returns:
            Handler class or None
        """
        with self._lock:
            return self._handlers.get(name.lower())

    def get_format_by_extension(self, extension: str) -> Optional[str]:
        """
        Get format name by file extension.

        Args:
            extension: File extension (with or without leading dot)

        Returns:
            Format name or None
        """
        with self._lock:
            return self._extensions.get(extension.lower().lstrip("."))

    def get_available_formats(self) -> List[str]:
        """
        Get list of all registered format names.

        Returns:
            List of format names
        """
        with self._lock:
            return list(self._handlers.keys())

    def has_handler(self, name: str) -> bool:
        """
        Check if a handler is registered.

        Args:
            name: Handler name (case-insensitive)

        Returns:
            True if handler exists
        """
        with self._lock:
            return name.lower() in self._handlers

    def unregister(self, name: str) -> bool:
        """
        Unregister a handler.

        Args:
            name: Handler name (case-insensitive)

        Returns:
            True if handler was removed, False if not found
        """
        with self._lock:
            name_lower = name.lower()
            if name_lower in self._handlers:
                del self._handlers[name_lower]

                # Remove associated extensions
                extensions_to_remove = [
                    ext
                    for ext, format_name in self._extensions.items()
                    if format_name == name_lower
                ]
                for ext in extensions_to_remove:
                    del self._extensions[ext]

                return True
            return False

    def clear(self) -> None:
        """Clear all registered handlers."""
        with self._lock:
            self._handlers.clear()
            self._extensions.clear()


class MethodGenerator:
    """
    Utility for thread-safe dynamic method generation.
    """

    @staticmethod
    def generate_export_methods(
        target_class: Type,
        factory: ThreadSafeFactory,
        method_template: Callable,
        method_name_pattern: str = "{action}_{format}",
        method_doc_pattern: str = "{action} data to {format} format.",
    ) -> None:
        """
        Generate dynamic methods on a class based on registered formats.

        Args:
            target_class: Class to add methods to
            factory: Factory containing registered formats
            method_template: Template function for generated methods
            method_name_pattern: Pattern for method names (supports {action}, {format})
            method_doc_pattern: Pattern for method docstrings
        """
        if not hasattr(factory, "_methods_lock"):
            return

        with factory._methods_lock:
            if getattr(factory, "_methods_generated", False):
                return  # Already generated

            logger.debug(f"Generating dynamic methods for {target_class.__name__}...")

            available_formats = factory.get_available_formats()
            for fmt_name in available_formats:
                safe_name = fmt_name.replace("-", "_").replace(".", "_")

                # Create method with proper closure
                def _make_method(captured_format: str) -> Callable:
                    def _method_impl(self_obj, *args, **kwargs) -> Any:
                        return method_template(
                            self_obj, captured_format, *args, **kwargs
                        )

                    return _method_impl

                method = _make_method(fmt_name)
                method_name = method_name_pattern.format(
                    action="export", format=safe_name
                )
                method.__name__ = method_name
                method.__doc__ = method_doc_pattern.format(
                    action="Export", format=fmt_name.upper()
                )

                # Only set if method doesn't already exist
                if not hasattr(target_class, method_name):
                    setattr(target_class, method_name, method)
                    logger.debug(
                        f"  Added method: {target_class.__name__}.{method_name}()"
                    )

            factory._methods_generated = True
            logger.debug("Finished generating dynamic methods.")
