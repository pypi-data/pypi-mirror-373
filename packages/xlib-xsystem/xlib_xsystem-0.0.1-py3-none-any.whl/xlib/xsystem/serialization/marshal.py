"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

Python Marshal Serializer Implementation

Provides Python marshal serialization with version control,
limited type support, and integration with xSystem utilities.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import marshal
import sys
from pathlib import Path

from .iSerialization import iSerialization
from .aSerialization import aSerialization


class MarshalSerializer(aSerialization):
    """
    Python Marshal serializer for simple Python objects.
    
    Features:
    - Fast Python-internal serialization
    - Limited but safe type support
    - Version control
    - Binary format
    - Python-specific
    - Security validation
    - Atomic file operations
    
    Note: Marshal only supports basic Python types and is mainly
    used for .pyc files. It's faster than pickle but more limited.
    """
    
    def __init__(
        self,
        version: int = marshal.version,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 100,
        max_size_mb: int = 50
    ) -> None:
        """
        Initialize Marshal serializer.
        
        Args:
            version: Marshal format version
            validate_input: Enable input data validation
            validate_paths: Enable path security validation
            use_atomic_writes: Use atomic file operations
            max_depth: Maximum nesting depth
            max_size_mb: Maximum data size in MB
        """
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )
        
        self._version = version
        
        # Supported types for marshal
        self._supported_types = {
            type(None), bool, int, float, complex, str, bytes, bytearray,
            tuple, list, set, frozenset, dict
        }
    
    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "Marshal"
    
    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".marshal", ".mar")
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-python-marshal"
    
    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return True
    
    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return False  # Marshal doesn't support streaming
    
    def _validate_marshal_data(self, data: Any, path: str = "root") -> None:
        """
        Validate that data contains only marshal-supported types.
        
        Args:
            data: Data to validate
            path: Current path in data structure (for error reporting)
            
        Raises:
            ValueError: If data contains unsupported types
        """
        data_type = type(data)
        
        if data_type not in self._supported_types:
            raise ValueError(
                f"Marshal does not support type {data_type.__name__} at {path}. "
                f"Supported types: {[t.__name__ for t in self._supported_types]}"
            )
        
        # Recursively validate containers
        if isinstance(data, (list, tuple)):
            for i, item in enumerate(data):
                self._validate_marshal_data(item, f"{path}[{i}]")
        elif isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(key, (str, int, float, bytes, tuple)):
                    raise ValueError(f"Marshal dict keys must be simple types, got {type(key).__name__} at {path}")
                self._validate_marshal_data(key, f"{path}.key({key})")
                self._validate_marshal_data(value, f"{path}[{key}]")
        elif isinstance(data, (set, frozenset)):
            for i, item in enumerate(data):
                self._validate_marshal_data(item, f"{path}.item({i})")
    
    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to marshal and return as base64-encoded string.
        
        Args:
            data: Data to serialize (must be marshal-compatible)
            
        Returns:
            Base64-encoded marshal string
            
        Raises:
            ValueError: If data validation fails or contains unsupported types
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        # Validate marshal compatibility
        self._validate_marshal_data(data)
        
        try:
            result = marshal.dumps(data, self._version)
            # Encode to base64 string for string interface
            import base64
            return base64.b64encode(result).decode('ascii')
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def loads_text(self, data: str) -> Any:
        """
        Deserialize marshal from base64-encoded string.
        
        Args:
            data: Base64-encoded marshal string to deserialize
            
        Returns:
            Deserialized data
            
        Raises:
            ValueError: If data is invalid or validation fails
        """
        try:
            # Decode base64 to bytes
            import base64
            marshal_bytes = base64.b64decode(data.encode('ascii'))
            
            result = marshal.loads(marshal_bytes)
            
            if self.validate_input:
                self._validate_data_security(result)
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)
    
    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to marshal bytes directly.
        
        Args:
            data: Data to serialize (must be marshal-compatible)
            
        Returns:
            Marshal bytes
            
        Raises:
            ValueError: If data validation fails or contains unsupported types
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        # Validate marshal compatibility
        self._validate_marshal_data(data)
        
        try:
            return marshal.dumps(data, self._version)
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def loads_bytes(self, data: bytes) -> Any:
        """
        Deserialize marshal bytes directly.
        
        Args:
            data: Marshal bytes to deserialize
            
        Returns:
            Deserialized data
            
        Raises:
            ValueError: If data is invalid or validation fails
        """
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError(f"Expected bytes or bytearray, got {type(data)}")
        
        try:
            result = marshal.loads(data)
            
            if self.validate_input:
                self._validate_data_security(result)
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)
    
    # 🎯 OPTIMIZATION: save_file and load_file inherited from base class!
    # Base class automatically handles binary format based on is_binary_format flag
    
    def get_supported_types(self) -> Set[type]:
        """
        Get set of types supported by marshal.
        
        Returns:
            Set of supported types
        """
        return self._supported_types.copy()
    
    def is_supported_type(self, obj: Any) -> bool:
        """
        Check if an object type is supported by marshal.
        
        Args:
            obj: Object to check
            
        Returns:
            True if type is supported
        """
        return type(obj) in self._supported_types
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get Marshal format schema information.
        
        Returns:
            Schema information dictionary
        """
        return {
            "format": "Marshal",
            "version": self._version,
            "description": "Python internal object serialization",
            "features": {
                "binary": True,
                "python_specific": True,
                "fast": True,
                "limited_types": True,
                "streaming": False,
                "safe": True
            },
            "supported_types": [t.__name__ for t in self._supported_types],
            "python_version": sys.version,
            "marshal_version": marshal.version,
            "file_extensions": list(self.file_extensions),
            "mime_type": self.mime_type
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current serializer configuration.
        
        Returns:
            Configuration dictionary
        """
        config = super().get_config()
        config.update({
            "version": self._version,
            "supported_types": [t.__name__ for t in self._supported_types]
        })
        return config


# Error classes for consistency with other serializers
class MarshalError(Exception):
    """Base exception for Marshal serialization errors."""
    pass
