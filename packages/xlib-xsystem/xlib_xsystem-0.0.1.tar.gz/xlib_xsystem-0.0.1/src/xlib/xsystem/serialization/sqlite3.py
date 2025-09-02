"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

SQLite3 Serializer Implementation

Provides SQLite database serialization using the built-in sqlite3 module
following the 'no hardcode' principle.
"""

import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .aSerialization import aSerialization, SerializationError


class Sqlite3Error(SerializationError):
    """SQLite3-specific serialization error."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "SQLite3", original_error)


class Sqlite3Serializer(aSerialization):
    """
    SQLite3 serializer using built-in sqlite3 module.
    
    This implementation strictly follows the 'no hardcode' principle by using
    only the built-in sqlite3 library for database operations.
    
    Features:
    - Uses sqlite3.connect for database operations
    - Binary format (SQLite database file)
    - Security validation
    - Atomic file operations
    - Supports tables, rows, and various data types
    """

    def __init__(
        self,
        table_name: str = "data",
        timeout: float = 5.0,
        isolation_level: Optional[str] = None,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 100,
        max_size_mb: int = 500  # SQLite can handle larger files
    ) -> None:
        """
        Initialize SQLite3 serializer.

        Args:
            table_name: Default table name for data storage
            timeout: Database connection timeout
            isolation_level: Transaction isolation level
            validate_input: Enable input data validation
            validate_paths: Enable path security validation
            use_atomic_writes: Use atomic file operations
            max_depth: Maximum nesting depth
            max_size_mb: Maximum database file size in MB
        """
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )

        self._table_name = table_name
        self._timeout = timeout
        self._isolation_level = isolation_level

    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "SQLite3"

    @property
    def file_extensions(self) -> Tuple[str, ...]:
        """Get supported file extensions."""
        return (".db", ".sqlite", ".sqlite3")

    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-sqlite3"

    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True  # SQLite supports streaming reads/writes

    def dumps(self, data: Any) -> bytes:
        """
        Serialize data to SQLite database in memory.

        ✅ PRODUCTION LIBRARY: sqlite3.connect()
        
        Args:
            data: Dictionary or list of dictionaries to store
            
        Returns:
            SQLite database as bytes
        """
        if self.validate_input:
            self._validate_data_security(data)

        try:
            # Create in-memory database
            conn = sqlite3.connect(
                ":memory:",
                timeout=self._timeout,
                isolation_level=self._isolation_level
            )
            
            # Convert data to list of dictionaries if needed
            if isinstance(data, dict):
                if all(isinstance(v, dict) for v in data.values()):
                    # Dict of dicts -> multiple rows
                    rows = [{"id": k, **v} for k, v in data.items()]
                else:
                    # Single dict -> single row
                    rows = [data]
            elif isinstance(data, list):
                rows = data
            else:
                # Single value -> single row
                rows = [{"value": data}]

            if not rows:
                raise Sqlite3Error("No data to serialize")

            # Create table based on first row structure
            first_row = rows[0]
            if not isinstance(first_row, dict):
                raise Sqlite3Error("Data must be dict or list of dicts")

            columns = list(first_row.keys())
            column_defs = ", ".join(f"{col} TEXT" for col in columns)
            
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE {self._table_name} ({column_defs})")
            
            # Insert data
            placeholders = ", ".join("?" * len(columns))
            insert_sql = f"INSERT INTO {self._table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            for row in rows:
                if not isinstance(row, dict):
                    raise Sqlite3Error(f"All rows must be dicts, got {type(row)}")
                
                # Convert values to JSON strings for complex types
                values = []
                for col in columns:
                    value = row.get(col)
                    if isinstance(value, (dict, list)):
                        values.append(json.dumps(value))
                    elif value is None:
                        values.append(None)
                    else:
                        values.append(str(value))
                
                cursor.execute(insert_sql, values)
            
            conn.commit()
            
            # Get database as bytes
            # SQLite backup to get the entire database
            backup_conn = sqlite3.connect(":memory:")
            conn.backup(backup_conn)
            
            # Read the backup database
            backup_conn.close()
            conn.close()
            
            # Since we can't directly get bytes from in-memory DB,
            # we'll use a temporary file approach
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                # Create file database
                file_conn = sqlite3.connect(
                    tmp_path,
                    timeout=self._timeout,
                    isolation_level=self._isolation_level
                )
                
                # Recreate table and data in file
                cursor = file_conn.cursor()
                cursor.execute(f"CREATE TABLE {self._table_name} ({column_defs})")
                
                for row in rows:
                    values = []
                    for col in columns:
                        value = row.get(col)
                        if isinstance(value, (dict, list)):
                            values.append(json.dumps(value))
                        elif value is None:
                            values.append(None)
                        else:
                            values.append(str(value))
                    
                    cursor.execute(insert_sql, values)
                
                file_conn.commit()
                file_conn.close()
                
                # Read file as bytes
                with open(tmp_path, 'rb') as f:
                    db_bytes = f.read()
                
                return db_bytes
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            self._handle_serialization_error("serialization", e)

    def loads(self, data: Union[bytes, str]) -> List[Dict[str, Any]]:
        """
        Deserialize SQLite database.

        ✅ PRODUCTION LIBRARY: sqlite3.connect()
        
        Args:
            data: SQLite database as bytes or file path as string
            
        Returns:
            List of dictionaries representing table rows
        """
        try:
            if isinstance(data, str):
                # Assume it's a file path
                conn = sqlite3.connect(
                    data,
                    timeout=self._timeout,
                    isolation_level=self._isolation_level
                )
            elif isinstance(data, bytes):
                # Write bytes to temp file and open
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(data)
                    tmp_path = tmp_file.name
                
                try:
                    conn = sqlite3.connect(
                        tmp_path,
                        timeout=self._timeout,
                        isolation_level=self._isolation_level
                    )
                finally:
                    # Schedule cleanup
                    import atexit
                    atexit.register(lambda: os.unlink(tmp_path) if os.path.exists(tmp_path) else None)
            else:
                raise Sqlite3Error(f"Expected bytes or string, got {type(data)}")

            # Set row factory to get dict-like rows
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all rows from the specified table
            cursor.execute(f"SELECT * FROM {self._table_name}")
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for row in rows:
                row_dict = {}
                for key in row.keys():
                    value = row[key]
                    # Try to parse JSON for complex types
                    if isinstance(value, str):
                        try:
                            parsed = json.loads(value)
                            row_dict[key] = parsed
                        except (json.JSONDecodeError, TypeError):
                            row_dict[key] = value
                    else:
                        row_dict[key] = value
                result.append(row_dict)
            
            conn.close()
            
            if self.validate_input:
                self._validate_data_security(result)
                
            return result

        except Exception as e:
            self._handle_serialization_error("deserialization", e)

    def save_file(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Save data to SQLite database file.
        
        🗄️ DATABASE FORMAT: SQLite3 overrides base class save_file() because it creates
        actual database files with connections, not just serialized data dumps.
        
        Args:
            data: Data to serialize
            file_path: Path to the database file
        """
        validated_path = self._validate_file_path(file_path)
        
        if self.validate_input:
            self._validate_data_security(data)
        
        try:
            # Create database directly at file path
            conn = sqlite3.connect(
                str(validated_path),
                timeout=self._timeout,
                isolation_level=self._isolation_level
            )
            
            # Process data similar to dumps()
            if isinstance(data, dict):
                if all(isinstance(v, dict) for v in data.values()):
                    rows = [{"id": k, **v} for k, v in data.items()]
                else:
                    rows = [data]
            elif isinstance(data, list):
                rows = data
            else:
                rows = [{"value": data}]

            if not rows:
                raise Sqlite3Error("No data to save")

            first_row = rows[0]
            if not isinstance(first_row, dict):
                raise Sqlite3Error("Data must be dict or list of dicts")

            columns = list(first_row.keys())
            column_defs = ", ".join(f"{col} TEXT" for col in columns)
            
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE {self._table_name} ({column_defs})")
            
            placeholders = ", ".join("?" * len(columns))
            insert_sql = f"INSERT INTO {self._table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            for row in rows:
                values = []
                for col in columns:
                    value = row.get(col)
                    if isinstance(value, (dict, list)):
                        values.append(json.dumps(value))
                    elif value is None:
                        values.append(None)
                    else:
                        values.append(str(value))
                
                cursor.execute(insert_sql, values)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self._handle_serialization_error("file save", e)

    def load_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load data from SQLite database file.
        
        🗄️ DATABASE FORMAT: SQLite3 overrides base class load_file() because it reads
        actual database files with connections, not just serialized data.
        
        Args:
            file_path: Path to the database file
            
        Returns:
            List of dictionaries representing table rows
        """
        validated_path = self._validate_file_path(file_path)
        return self.loads(str(validated_path))

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get SQLite3 format schema information.

        Returns:
            Schema information dictionary
        """
        return {
            "format": "SQLite3",
            "version": "3.0",
            "description": "SQLite database (using built-in sqlite3)",
            "features": {
                "binary": True,
                "tables": True,
                "sql_queries": True,
                "transactions": True,
                "indexes": True,
                "streaming": True,
                "secure_parsing": True
            },
            "supported_types": [
                "tables", "rows", "columns", "sql_data_types"
            ],
            "table_name": self._table_name,
            "timeout": self._timeout,
            "isolation_level": self._isolation_level,
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
            "table_name": self._table_name,
            "timeout": self._timeout,
            "isolation_level": self._isolation_level
        })
        return config
