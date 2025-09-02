"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 31, 2025

xSystem Serialization Package

Provides comprehensive serialization utilities for 17 formats following the production library principle.

🚨 CRITICAL PRINCIPLE: NO HARDCODED SERIALIZATION LOGIC
   All serializers use established, well-tested libraries only!

📊 FORMAT BREAKDOWN:

TEXT FORMATS (8):
1. JSON        - Built-in json library
2. YAML        - PyYAML library 
3. TOML        - Built-in tomllib + tomli-w
4. XML         - dicttoxml + xmltodict libraries
5. CSV         - Built-in csv library
6. ConfigParser- Built-in configparser module
7. FormData    - Built-in urllib.parse
8. Multipart   - Built-in email.mime modules

BINARY FORMATS (9):
9.  BSON       - pymongo.bson library
10. MessagePack- msgpack library
11. CBOR       - cbor2 library
12. Pickle     - Built-in pickle module
13. Marshal    - Built-in marshal module
14. SQLite3    - Built-in sqlite3 module
15. DBM        - Built-in dbm module
16. Shelve     - Built-in shelve module
17. Plistlib   - Built-in plistlib module

✅ BENEFITS:
- ONE import gets 17 serialization formats
- Production-grade reliability (no custom parsers)
- Consistent API across all formats
- Security validation & atomic file operations
- Minimizes dependencies in consuming projects
"""

from .iSerialization import iSerialization
from .aSerialization import aSerialization, SerializationError

# Core 12 formats (established external + built-in libraries)
from .json import JsonSerializer, JsonError
from .yaml import YamlSerializer, YamlError
from .toml import TomlSerializer, TomlError
from .xml import XmlSerializer, XmlError
from .bson import BsonSerializer, BsonError
from .msgpack import MsgPackSerializer
from .cbor import CborSerializer, CborError
from .csv import CsvSerializer, CsvError
from .pickle import PickleSerializer, PickleError
from .marshal import MarshalSerializer, MarshalError
from .formdata import FormDataSerializer, FormDataError
from .multipart import MultipartSerializer, MultipartError

# Built-in Python modules (5 additional formats)
from .configparser import ConfigParserSerializer, ConfigParserError
from .sqlite3 import Sqlite3Serializer, Sqlite3Error
from .dbm import DbmSerializer, DbmError
from .shelve import ShelveSerializer, ShelveError
from .plistlib import PlistlibSerializer, PlistlibError

__all__ = [
    # Interface and base class
    "iSerialization",
    "aSerialization", 
    "SerializationError",
    # Core 12 formats
    "JsonSerializer", "JsonError", 
    "YamlSerializer", "YamlError",
    "TomlSerializer", "TomlError",
    "XmlSerializer", "XmlError",
    "BsonSerializer", "BsonError",
    "MsgPackSerializer",
    "CborSerializer", "CborError",
    "CsvSerializer", "CsvError",
    "PickleSerializer", "PickleError",
    "MarshalSerializer", "MarshalError",
    "FormDataSerializer", "FormDataError",
    "MultipartSerializer", "MultipartError",
    # Built-in Python modules (5 additional formats)
    "ConfigParserSerializer", "ConfigParserError",
    "Sqlite3Serializer", "Sqlite3Error",
    "DbmSerializer", "DbmError",
    "ShelveSerializer", "ShelveError",
    "PlistlibSerializer", "PlistlibError",
]
