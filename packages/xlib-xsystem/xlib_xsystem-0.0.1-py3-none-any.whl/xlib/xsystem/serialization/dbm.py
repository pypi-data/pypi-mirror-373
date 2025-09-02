"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

DBM Serializer Implementation

Provides DBM (Database Manager) serialization using the built-in dbm module
following the 'no hardcode' principle.
"""

import dbm
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from .aSerialization import aSerialization, SerializationError


class DbmError(SerializationError):
    """DBM-specific serialization error."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "DBM", original_error)


class DbmSerializer(aSerialization):
    """
    DBM serializer using built-in dbm module.
    
    This implementation strictly follows the 'no hardcode' principle by using
    only the built-in dbm library for key-value database operations.
    
    Features:
    - Uses dbm.open for database operations
    - Binary format (platform-dependent dbm files)
    - Security validation
    - Key-value store semantics
    - Supports various dbm backends (ndbm, gdbm, etc.)
    
    Note: DBM is optional based on platform availability
    """

    def __init__(
        self,
        flag: str = 'c',  # 'r'=read, 'w'=write, 'c'=create, 'n'=new
        mode: int = 0o666,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 100,
        max_size_mb: int = 100
    ) -> None:
        """
        Initialize DBM serializer.

        Args:
            flag: Database open flag ('r', 'w', 'c', 'n')
            mode: File mode for database creation
            validate_input: Enable input data validation
            validate_paths: Enable path security validation
            use_atomic_writes: Use atomic file operations
            max_depth: Maximum nesting depth
            max_size_mb: Maximum database size in MB
        """
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )

        self._flag = flag
        self._mode = mode

    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "DBM"

    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".db", ".dbm", ".gdbm", ".ndbm")

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-dbm"

    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True  # DBM supports key-by-key access

    def dumps(self, data: Any) -> bytes:
        """
        Serialize data to DBM database in memory (simulated with temp file).

        ✅ PRODUCTION LIBRARY: dbm.open()
        
        Args:
            data: Dictionary to store as key-value pairs
            
        Returns:
            DBM database content as bytes (base64 encoded)
        """
        if self.validate_input:
            self._validate_data_security(data)

        if not isinstance(data, dict):
            raise DbmError(f"DBM requires dict data, got {type(data)}")

        try:
            import tempfile
            import os
            import base64
            import shutil

            # Create temporary directory for DBM files
            with tempfile.TemporaryDirectory() as temp_dir:
                db_path = os.path.join(temp_dir, "temp_db")
                
                # Open DBM database
                with dbm.open(db_path, 'n', self._mode) as db:
                    for key, value in data.items():
                        # Convert key and value to bytes
                        key_bytes = str(key).encode('utf-8')
                        
                        if isinstance(value, (dict, list)):
                            value_bytes = json.dumps(value).encode('utf-8')
                        elif isinstance(value, str):
                            value_bytes = value.encode('utf-8')
                        elif isinstance(value, bytes):
                            value_bytes = value
                        elif value is None:
                            value_bytes = b''
                        else:
                            value_bytes = str(value).encode('utf-8')
                        
                        db[key_bytes] = value_bytes
                
                # Collect all DBM files (platform dependent)
                db_files = []
                for file in os.listdir(temp_dir):
                    if file.startswith("temp_db"):
                        file_path = os.path.join(temp_dir, file)
                        with open(file_path, 'rb') as f:
                            db_files.append((file, f.read()))
                
                # Create a simple archive format: filename_length:filename:content_length:content
                result = b''
                for filename, content in db_files:
                    filename_bytes = filename.encode('utf-8')
                    result += len(filename_bytes).to_bytes(4, 'big')
                    result += filename_bytes
                    result += len(content).to_bytes(8, 'big')
                    result += content
                
                return result

        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> Dict[str, Any]:
        """
        Deserialize DBM database.

        ✅ PRODUCTION LIBRARY: dbm.open()
        
        Args:
            data: DBM database as bytes or file path as string
            
        Returns:
            Dictionary with key-value pairs
        """
        try:
            if isinstance(data, str):
                # Assume it's a file path
                with dbm.open(data, 'r') as db:
                    result = {}
                    for key_bytes in db.keys():
                        value_bytes = db[key_bytes]
                        
                        # Convert bytes back to strings
                        key = key_bytes.decode('utf-8')
                        value_str = value_bytes.decode('utf-8')
                        
                        # Try to parse as JSON for complex types
                        try:
                            value = json.loads(value_str)
                        except (json.JSONDecodeError, TypeError):
                            value = value_str if value_str else None
                        
                        result[key] = value
                    
                    if self.validate_input:
                        self._validate_data_security(result)
                        
                    return result
                    
            elif isinstance(data, bytes):
                # Restore from our archive format
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Parse archive format
                    offset = 0
                    while offset < len(data):
                        if offset + 4 > len(data):
                            break
                        
                        filename_length = int.from_bytes(data[offset:offset+4], 'big')
                        offset += 4
                        
                        if offset + filename_length > len(data):
                            break
                        
                        filename = data[offset:offset+filename_length].decode('utf-8')
                        offset += filename_length
                        
                        if offset + 8 > len(data):
                            break
                        
                        content_length = int.from_bytes(data[offset:offset+8], 'big')
                        offset += 8
                        
                        if offset + content_length > len(data):
                            break
                        
                        content = data[offset:offset+content_length]
                        offset += content_length
                        
                        # Write file
                        file_path = os.path.join(temp_dir, filename)
                        with open(file_path, 'wb') as f:
                            f.write(content)
                    
                    # Open the main database file
                    db_path = os.path.join(temp_dir, "temp_db")
                    if not os.path.exists(db_path):
                        # Try to find any file that looks like a DBM file
                        for file in os.listdir(temp_dir):
                            if file.startswith("temp_db"):
                                db_path = os.path.join(temp_dir, file.split('.')[0])
                                break
                    
                    with dbm.open(db_path, 'r') as db:
                        result = {}
                        for key_bytes in db.keys():
                            value_bytes = db[key_bytes]
                            
                            key = key_bytes.decode('utf-8')
                            value_str = value_bytes.decode('utf-8')
                            
                            try:
                                value = json.loads(value_str)
                            except (json.JSONDecodeError, TypeError):
                                value = value_str if value_str else None
                            
                            result[key] = value
                        
                        if self.validate_input:
                            self._validate_data_security(result)
                            
                        return result
            else:
                raise DbmError(f"Expected bytes or string, got {type(data)}")

        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def save_file(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Save data to DBM database file.
        
        🗄️ DATABASE FORMAT: DBM overrides base class save_file() because it creates
        actual key-value database files, not just serialized data dumps.
        
        Args:
            data: Dictionary to store
            file_path: Path to the database file
        """
        validated_path = self._validate_file_path(file_path)
        
        if self.validate_input:
            self._validate_data_security(data)
        
        if not isinstance(data, dict):
            raise DbmError(f"DBM requires dict data, got {type(data)}")
        
        try:
            with dbm.open(str(validated_path), self._flag, self._mode) as db:
                for key, value in data.items():
                    key_bytes = str(key).encode('utf-8')
                    
                    if isinstance(value, (dict, list)):
                        value_bytes = json.dumps(value).encode('utf-8')
                    elif isinstance(value, str):
                        value_bytes = value.encode('utf-8')
                    elif isinstance(value, bytes):
                        value_bytes = value
                    elif value is None:
                        value_bytes = b''
                    else:
                        value_bytes = str(value).encode('utf-8')
                    
                    db[key_bytes] = value_bytes
            
        except Exception as e:
            self._handle_serialization_error("file save", e)

    def load_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load data from DBM database file.
        
        🗄️ DATABASE FORMAT: DBM overrides base class load_file() because it reads
        actual key-value database files, not just serialized data.
        
        Args:
            file_path: Path to the database file
            
        Returns:
            Dictionary with key-value pairs
        """
        validated_path = self._validate_file_path(file_path)
        return self.loads(str(validated_path))

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get DBM format schema information.

        Returns:
            Schema information dictionary
        """
        return {
            "format": "DBM",
            "version": "1.0",
            "description": "Database Manager key-value store (using built-in dbm)",
            "features": {
                "binary": True,
                "key_value": True,
                "persistent": True,
                "platform_dependent": True,
                "streaming": True,
                "secure_parsing": True
            },
            "supported_types": [
                "key_value_pairs", "strings", "bytes"
            ],
            "flag": self._flag,
            "mode": self._mode,
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
            "flag": self._flag,
            "mode": self._mode
        })
        return config
