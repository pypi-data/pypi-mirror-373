"""
I/O utilities for safe file operations and path management.
"""

from .atomic_file import (
    AtomicFileWriter,
    FileOperationError,
    safe_read_bytes,
    safe_read_text,
    safe_read_with_fallback,
    safe_write_bytes,
    safe_write_text,
)
from .path_manager import PathManager

__all__ = [
    "AtomicFileWriter",
    "FileOperationError",
    "safe_write_text",
    "safe_write_bytes",
    "safe_read_text",
    "safe_read_bytes",
    "safe_read_with_fallback",
    "PathManager",
]
