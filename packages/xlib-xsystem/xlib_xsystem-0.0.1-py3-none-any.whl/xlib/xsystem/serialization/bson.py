"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Enhanced BSON serialization with security, validation and performance optimizations.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

try:
    import bson
    from bson import ObjectId, Binary
    BSON_AVAILABLE = True
except ImportError:
    BSON_AVAILABLE = False

from .aSerialization import aSerialization, SerializationError
from ..config.logging_setup import get_logger
from ..io.atomic_file import AtomicFileWriter

logger = get_logger("xsystem.serialization.bson")


class BsonError(SerializationError):
    """BSON-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "BSON", original_error)


class BsonSerializer(aSerialization):
    """
    Enhanced BSON serializer with security validation and xSystem integration.
    
    BSON (Binary JSON) is primarily used by MongoDB and supports additional
    data types like ObjectId, Binary, DateTime, etc.
    """

    def __init__(
        self,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 16.0,  # BSON documents can be larger than JSON
        encode_to_utf8: bool = True,
        check_keys: bool = True,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Initialize BSON serializer with security and performance options.

        Args:
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            encode_to_utf8: Whether to encode strings to UTF-8
            check_keys: Whether to check that keys are valid
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
        """
        if not BSON_AVAILABLE:
            raise BsonError("bson is required for BSON serialization. Install with: pip install pymongo")
            
        # Initialize base class with xSystem integration
        super().__init__(
            validate_input=validate_input,
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            use_atomic_writes=use_atomic_writes,
            validate_paths=validate_paths,
            base_path=base_path,
        )
        
        # BSON-specific configuration
        self.encode_to_utf8 = encode_to_utf8
        self.check_keys = check_keys
        
        # Update configuration with BSON-specific options
        self._config.update({
            'encode_to_utf8': encode_to_utf8,
            'check_keys': check_keys,
        })

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "BSON"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return ['.bson']

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/bson"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def _prepare_for_bson(self, data: Any) -> Any:
        """Prepare data for BSON serialization by converting unsupported types."""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if not isinstance(key, str):
                    key = str(key)
                result[key] = self._prepare_for_bson(value)
            return result
        elif isinstance(data, list):
            return [self._prepare_for_bson(item) for item in data]
        elif isinstance(data, tuple):
            return [self._prepare_for_bson(item) for item in data]
        elif isinstance(data, set):
            return [self._prepare_for_bson(item) for item in data]
        elif isinstance(data, bytes):
            return Binary(data)
        elif isinstance(data, (int, float, str, bool, type(None))):
            return data
        elif isinstance(data, datetime):
            return data
        else:
            # Convert other types to string representation
            logger.warning(f"Converting unsupported type {type(data)} to string for BSON")
            return str(data)

    def dumps(self, data: Any) -> str:
        """
        Serialize data to BSON and return as base64-encoded string.

        Args:
            data: Data to serialize

        Returns:
            Base64-encoded BSON string

        Raises:
            BsonError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            
            # Prepare data for BSON
            prepared_data = self._prepare_for_bson(data)
            
            # Serialize to BSON bytes
            bson_bytes = bson.encode(prepared_data)
            
            # Encode to base64 string for string interface
            import base64
            return base64.b64encode(bson_bytes).decode('ascii')
            
        except SerializationError as e:
            # Use unified error handling to include format name
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            # Use unified error handling to include format name
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Any:
        """
        Deserialize BSON bytes to Python object.

        Args:
            data: BSON bytes or base64-encoded string to deserialize

        Returns:
            Deserialized Python object

        Raises:
            BsonError: If deserialization fails
        """
        try:
            # Handle both bytes and base64 string for backward compatibility
            if isinstance(data, str):
                # Decode base64 to bytes
                import base64
                bson_bytes = base64.b64decode(data.encode('ascii'))
            else:
                # Already bytes
                bson_bytes = data
            
            # Decode BSON
            result = bson.decode(bson_bytes)
            return result
            
        except Exception as e:
            # Use unified error handling to include format name
            self._handle_serialization_error("deserialization", e)

    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to BSON bytes directly.

        Args:
            data: Data to serialize

        Returns:
            BSON bytes

        Raises:
            BsonError: If serialization fails
        """
        try:
            # Validate data using base class
            self._validate_data_security(data)
            
            # Prepare data for BSON
            prepared_data = self._prepare_for_bson(data)
            
            # Serialize to BSON bytes
            return bson.encode(prepared_data)
            
        except SerializationError as e:
            # Use unified error handling to include format name
            self._handle_serialization_error("serialization", e)
        except Exception as e:
            # Use unified error handling to include format name
            self._handle_serialization_error("serialization", e)

    def loads_bytes(self, data: bytes) -> Any:
        """
        Deserialize BSON bytes to Python object.

        Args:
            data: BSON bytes to deserialize

        Returns:
            Deserialized Python object

        Raises:
            BsonError: If deserialization fails
        """
        try:
            return bson.decode(data)
        except Exception as e:
            # Use unified error handling to include format name
            self._handle_serialization_error("deserialization", e)

    # 🎯 OPTIMIZATION: save_file and load_file inherited from base class!
    # Base class automatically handles binary format based on is_binary_format flag
    # No need for separate save_file_binary/load_file_binary methods


# Convenience functions for common use cases
def dumps(data: Any, **kwargs: Any) -> str:
    """Serialize data to BSON base64-encoded string with default settings."""
    serializer = BsonSerializer(**kwargs)
    return serializer.dumps(data)


def loads(s: str, **kwargs: Any) -> Any:
    """Deserialize BSON string with default settings.""" 
    serializer = BsonSerializer(**kwargs)
    return serializer.loads(s)


def dumps_bytes(data: Any, **kwargs: Any) -> bytes:
    """Serialize data to BSON bytes with default settings."""
    serializer = BsonSerializer(**kwargs)
    return serializer.dumps_binary(data)


def loads_bytes(data: bytes, **kwargs: Any) -> Any:
    """Deserialize BSON bytes with default settings."""
    serializer = BsonSerializer(**kwargs)
    return serializer.loads_bytes(data)


def load_file(file_path: Union[str, Path], **kwargs: Any) -> Any:
    """Load BSON from file with default settings."""
    serializer = BsonSerializer(**kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], **kwargs: Any) -> None:
    """Save data to BSON file with default settings."""
    serializer = BsonSerializer(**kwargs)
    return serializer.save_file(data, file_path)


# 🎯 OPTIMIZATION: Binary file operations now handled by standard save_file/load_file
# Base class automatically detects binary format and uses appropriate I/O methods
