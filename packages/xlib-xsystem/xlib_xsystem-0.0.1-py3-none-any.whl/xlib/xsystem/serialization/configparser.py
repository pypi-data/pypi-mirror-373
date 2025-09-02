"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

ConfigParser Serializer Implementation

Provides INI file serialization using the built-in configparser module
following the 'no hardcode' principle.
"""

import configparser
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from .aSerialization import aSerialization, SerializationError


class ConfigParserError(SerializationError):
    """ConfigParser-specific serialization error."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "ConfigParser", original_error)


class ConfigParserSerializer(aSerialization):
    """
    ConfigParser serializer using built-in configparser module.
    
    This implementation strictly follows the 'no hardcode' principle by using
    only the built-in configparser library for INI file handling.
    
    Features:
    - Uses configparser.ConfigParser for INI file parsing/writing
    - Text format
    - Security validation
    - Atomic file operations
    - Supports sections and key-value pairs
    """

    def __init__(
        self,
        allow_no_value: bool = False,
        delimiters: Tuple[str, ...] = ('=', ':'),
        comment_prefixes: Tuple[str, ...] = ('#', ';'),
        interpolation: Optional[configparser.Interpolation] = None,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 100,
        max_size_mb: int = 50
    ) -> None:
        """
        Initialize ConfigParser serializer.

        Args:
            allow_no_value: Allow options without values
            delimiters: Key-value delimiters
            comment_prefixes: Comment line prefixes
            interpolation: Value interpolation handler
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

        self._allow_no_value = allow_no_value
        self._delimiters = delimiters
        self._comment_prefixes = comment_prefixes
        self._interpolation = interpolation

    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "ConfigParser"

    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".ini", ".cfg", ".conf")

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "text/plain"

    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return False

    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return False

    def dumps(self, data: Any) -> str:
        """
        Serialize data to INI format using configparser.

        ✅ PRODUCTION LIBRARY: configparser.ConfigParser()
        
        Args:
            data: Dictionary with sections and key-value pairs
            
        Returns:
            INI format string
        """
        if self.validate_input:
            self._validate_data_security(data)

        if not isinstance(data, dict):
            raise ConfigParserError(f"Expected dict, got {type(data)}")

        try:
            config = configparser.ConfigParser(
                allow_no_value=self._allow_no_value,
                delimiters=self._delimiters,
                comment_prefixes=self._comment_prefixes,
                interpolation=self._interpolation
            )
            
            # Add sections and options
            for section_name, section_data in data.items():
                if not isinstance(section_data, dict):
                    raise ConfigParserError(f"Section '{section_name}' must be a dict, got {type(section_data)}")
                
                config.add_section(section_name)
                for key, value in section_data.items():
                    # Convert values to strings as required by configparser
                    config.set(section_name, str(key), str(value) if value is not None else '')

            # Write to string
            from io import StringIO
            output = StringIO()
            config.write(output)
            return output.getvalue()

        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Dict[str, Dict[str, str]]:
        """
        Deserialize INI format using configparser.

        ✅ PRODUCTION LIBRARY: configparser.ConfigParser()
        
        Args:
            data: INI format string or bytes
            
        Returns:
            Dictionary with sections and key-value pairs
        """
        if isinstance(data, bytes):
            data = data.decode('utf-8')

        if not isinstance(data, str):
            raise ConfigParserError(f"Expected string or bytes, got {type(data)}")

        try:
            config = configparser.ConfigParser(
                allow_no_value=self._allow_no_value,
                delimiters=self._delimiters,
                comment_prefixes=self._comment_prefixes,
                interpolation=self._interpolation
            )
            
            config.read_string(data)
            
            # Convert to dictionary
            result = {}
            for section_name in config.sections():
                result[section_name] = dict(config.items(section_name))
            
            if self.validate_input:
                self._validate_data_security(result)
                
            return result

        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get ConfigParser format schema information.

        Returns:
            Schema information dictionary
        """
        return {
            "format": "ConfigParser",
            "version": "1.0",
            "description": "INI file format (using built-in configparser)",
            "features": {
                "binary": False,
                "sections": True,
                "key_value_pairs": True,
                "comments": True,
                "interpolation": self._interpolation is not None,
                "streaming": False,
                "secure_parsing": True
            },
            "supported_types": [
                "sections", "options", "string_values", "comments"
            ],
            "delimiters": list(self._delimiters),
            "comment_prefixes": list(self._comment_prefixes),
            "allow_no_value": self._allow_no_value,
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
            "allow_no_value": self._allow_no_value,
            "delimiters": self._delimiters,
            "comment_prefixes": self._comment_prefixes,
            "interpolation": str(self._interpolation) if self._interpolation else None
        })
        return config
