"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Enhanced JSON serialization with security, validation and performance optimizations.
"""

import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TextIO

from .aSerialization import aSerialization, SerializationError
from ..config.logging_setup import get_logger

logger = get_logger("xsystem.serialization.json")


class JsonError(SerializationError):
    """JSON-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "JSON", original_error)


class JsonSerializer(aSerialization):
    """
    Enhanced JSON serializer with security validation, custom encoders,
    and performance optimizations for production use.
    """

    def __init__(
        self,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 10.0,
        indent: Optional[int] = None,
        sort_keys: bool = False,
        ensure_ascii: bool = False,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Initialize JSON serializer with security and performance options.

        Args:
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            indent: JSON indentation for pretty printing
            sort_keys: Whether to sort dictionary keys
            ensure_ascii: Whether to escape non-ASCII characters
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
        """
        # Initialize base class with xSystem integration
        super().__init__(
            validate_input=validate_input,
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            use_atomic_writes=use_atomic_writes,
            validate_paths=validate_paths,
            base_path=base_path,
        )
        
        # JSON-specific configuration
        self.indent = indent
        self.sort_keys = sort_keys
        self.ensure_ascii = ensure_ascii
        
        # Update configuration with JSON-specific options
        self._config.update({
            'indent': indent,
            'sort_keys': sort_keys,
            'ensure_ascii': ensure_ascii,
        })

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "JSON"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.json']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/json"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return False

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def _validate_data(self, data: Any) -> None:
        """Validate data before serialization using base class validation."""
        try:
            self._validate_data_security(data)
        except SerializationError as e:
            raise JsonError(str(e), e.original_error) from e

    def _custom_encoder(self, obj: Any) -> Any:
        """Custom encoder for non-standard types."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to JSON string.

        Args:
            data: Data to serialize

        Returns:
            JSON string

        Raises:
            JsonError: If serialization fails
        """
        try:
            self._validate_data(data)
            
            return json.dumps(
                data,
                default=self._custom_encoder,
                indent=self.indent,
                sort_keys=self.sort_keys,
                ensure_ascii=self.ensure_ascii,
                separators=(',', ':') if self.indent is None else None
            )
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads_text(self, data: str) -> Any:
        """
        Deserialize JSON string to Python object.

        Args:
            data: JSON string to deserialize

        Returns:
            Deserialized Python object

        Raises:
            JsonError: If deserialization fails
        """
        try:
            result = json.loads(data)
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)


# Convenience functions for common use cases
def dumps(data: Any, **kwargs: Any) -> str:
    """Serialize data to JSON string with default settings."""
    serializer = JsonSerializer(**kwargs)
    return serializer.dumps(data)


def loads(s: str, **kwargs: Any) -> Any:
    """Deserialize JSON string with default settings.""" 
    serializer = JsonSerializer(**kwargs)
    return serializer.loads(s)


def load_file(file_path: Union[str, Path], **kwargs: Any) -> Any:
    """Load JSON from file with default settings."""
    serializer = JsonSerializer(**kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], **kwargs: Any) -> None:
    """Save data to JSON file with default settings."""
    serializer = JsonSerializer(**kwargs)
    return serializer.save_file(data, file_path)
