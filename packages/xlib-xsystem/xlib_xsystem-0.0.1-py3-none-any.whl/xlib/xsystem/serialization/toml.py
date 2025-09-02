"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Enhanced TOML serialization with security, validation and performance optimizations.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TextIO

# Hybrid approach: built-in tomllib for reading + tomli-w for writing
TOML_READ_AVAILABLE = sys.version_info >= (3, 11)
TOML_WRITE_AVAILABLE = False

if TOML_READ_AVAILABLE:
    import tomllib
else:
    tomllib = None

try:
    import tomli_w
    TOML_WRITE_AVAILABLE = True
except ImportError:
    tomli_w = None

TOML_AVAILABLE = TOML_READ_AVAILABLE and TOML_WRITE_AVAILABLE

from .aSerialization import aSerialization, SerializationError
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.toml")


class TomlError(SerializationError):
    """TOML-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "TOML", original_error)


class TomlSerializer(aSerialization):
    """
    Enhanced TOML serializer with security validation and xSystem integration.
    
    TOML (Tom's Obvious, Minimal Language) is primarily used for configuration files.
    This implementation provides secure parsing and generation with validation.
    """

    def __init__(
        self,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 10.0,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Initialize TOML serializer with security and performance options.

        Args:
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
        """
        if not TOML_AVAILABLE:
            raise TomlError("tomli and tomli-w are required for TOML serialization. Install with: pip install tomli tomli-w")
            
        # Initialize base class with xSystem integration
        super().__init__(
            validate_input=validate_input,
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            use_atomic_writes=use_atomic_writes,
            validate_paths=validate_paths,
            base_path=base_path,
        )

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "TOML"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.toml', '.tml']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/toml"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return False

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return False  # TOML requires complete parsing

    def _validate_toml_data(self, data: Any) -> None:
        """Validate data for TOML compatibility."""
        if not isinstance(data, dict):
            raise TomlError("TOML root must be a dictionary/table")
        
        # TOML has specific data type restrictions
        self._validate_toml_types(data)

    def _validate_toml_types(self, obj: Any, path: str = "") -> None:
        """Recursively validate TOML-compatible types."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if not isinstance(key, str):
                    raise TomlError(f"TOML keys must be strings, got {type(key)} at {path}.{key}")
                self._validate_toml_types(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            if obj:  # Non-empty list
                first_type = type(obj[0])
                for i, item in enumerate(obj):
                    if not isinstance(item, first_type):
                        raise TomlError(f"TOML arrays must be homogeneous, mixed types at {path}[{i}]")
                    if isinstance(item, (dict, list)):
                        self._validate_toml_types(item, f"{path}[{i}]")
        elif not isinstance(obj, (str, int, float, bool, bytes)):
            # TOML also supports datetime, but we'll be more restrictive for security
            raise TomlError(f"Unsupported TOML type {type(obj)} at {path}")

    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to TOML string.

        Args:
            data: Data to serialize (must be a dictionary)

        Returns:
            TOML string

        Raises:
            TomlError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            
            # TOML-specific validation
            self._validate_toml_data(data)
            
            # Serialize to TOML using tomli-w (best-in-class TOML writer)
            if not TOML_WRITE_AVAILABLE:
                raise TomlError("TOML writing requires 'tomli-w' package. Install with: pip install tomli-w")
            
            return tomli_w.dumps(data)
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads_text(self, data: str) -> Any:
        """
        Deserialize TOML string to Python object.

        Args:
            data: TOML string to deserialize

        Returns:
            Deserialized Python dictionary

        Raises:
            TomlError: If deserialization fails
        """
        try:
            result = tomllib.loads(data)
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)


# Convenience functions for common use cases
def dumps(data: Any, **kwargs: Any) -> str:
    """Serialize data to TOML string with default settings."""
    serializer = TomlSerializer(**kwargs)
    return serializer.dumps(data)


def loads(s: str, **kwargs: Any) -> Any:
    """Deserialize TOML string with default settings.""" 
    serializer = TomlSerializer(**kwargs)
    return serializer.loads(s)


def load_file(file_path: Union[str, Path], **kwargs: Any) -> Any:
    """Load TOML from file with default settings."""
    serializer = TomlSerializer(**kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], **kwargs: Any) -> None:
    """Save data to TOML file with default settings."""
    serializer = TomlSerializer(**kwargs)
    return serializer.save_file(data, file_path)
