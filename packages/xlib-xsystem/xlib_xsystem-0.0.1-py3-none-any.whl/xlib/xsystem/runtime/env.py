"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Environment management utilities for runtime configuration and detection.
"""

import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.runtime.env")


class EnvironmentManager:
    """
    Comprehensive environment management for runtime configuration,
    platform detection, and environment variable handling.
    """

    def __init__(self) -> None:
        """Initialize environment manager."""
        self._cache: Dict[str, Any] = {}
        self._env_vars: Dict[str, str] = dict(os.environ)

    @property
    def platform_info(self) -> Dict[str, str]:
        """Get comprehensive platform information."""
        if 'platform_info' not in self._cache:
            self._cache['platform_info'] = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'python_version': platform.python_version(),
                'python_implementation': platform.python_implementation(),
                'node': platform.node(),
            }
        return self._cache['platform_info']

    @property
    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return platform.system().lower() == 'windows'

    @property
    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return platform.system().lower() == 'linux'

    @property
    def is_macos(self) -> bool:
        """Check if running on macOS."""
        return platform.system().lower() == 'darwin'

    @property
    def is_64bit(self) -> bool:
        """Check if running on 64-bit architecture."""
        return platform.architecture()[0] == '64bit'

    @property
    def python_info(self) -> Dict[str, Any]:
        """Get Python runtime information."""
        if 'python_info' not in self._cache:
            self._cache['python_info'] = {
                'version': sys.version,
                'version_info': {
                    'major': sys.version_info.major,
                    'minor': sys.version_info.minor,
                    'micro': sys.version_info.micro,
                    'releaselevel': sys.version_info.releaselevel,
                    'serial': sys.version_info.serial,
                },
                'executable': sys.executable,
                'prefix': sys.prefix,
                'exec_prefix': sys.exec_prefix,
                'path': sys.path.copy(),
                'platform': sys.platform,
                'maxsize': sys.maxsize,
                'modules': list(sys.modules.keys()),
            }
        return self._cache['python_info']

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with optional default.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return self._env_vars.get(key, default)

    def get_env_bool(self, key: str, default: bool = False) -> bool:
        """
        Get environment variable as boolean.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Boolean value of environment variable
        """
        value = self.get_env(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')

    def get_env_int(self, key: str, default: int = 0) -> int:
        """
        Get environment variable as integer.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Integer value of environment variable
        """
        value = self.get_env(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
            return default

    def get_env_float(self, key: str, default: float = 0.0) -> float:
        """
        Get environment variable as float.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Float value of environment variable
        """
        value = self.get_env(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float value for {key}: {value}, using default: {default}")
            return default

    def get_env_list(self, key: str, separator: str = ',', default: Optional[List[str]] = None) -> List[str]:
        """
        Get environment variable as list.

        Args:
            key: Environment variable name
            separator: List item separator
            default: Default value if not found

        Returns:
            List of string values
        """
        value = self.get_env(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(separator) if item.strip()]

    def set_env(self, key: str, value: str) -> None:
        """
        Set environment variable.

        Args:
            key: Environment variable name
            value: Environment variable value
        """
        os.environ[key] = value
        self._env_vars[key] = value

    def unset_env(self, key: str) -> bool:
        """
        Unset environment variable.

        Args:
            key: Environment variable name

        Returns:
            True if variable was removed, False if it didn't exist
        """
        if key in os.environ:
            del os.environ[key]
        if key in self._env_vars:
            del self._env_vars[key]
            return True
        return False

    def get_user_home(self) -> Path:
        """Get user home directory."""
        return Path.home()

    def get_user_config_dir(self, app_name: Optional[str] = None) -> Path:
        """
        Get user configuration directory.

        Args:
            app_name: Application name for subdirectory

        Returns:
            Path to configuration directory
        """
        if self.is_windows:
            base = Path(self.get_env('APPDATA', ''))
            if not base:
                base = self.get_user_home() / 'AppData' / 'Roaming'
        elif self.is_macos:
            base = self.get_user_home() / 'Library' / 'Application Support'
        else:  # Linux and others
            base = Path(self.get_env('XDG_CONFIG_HOME', ''))
            if not base:
                base = self.get_user_home() / '.config'

        if app_name:
            base = base / app_name

        return base

    def get_user_data_dir(self, app_name: Optional[str] = None) -> Path:
        """
        Get user data directory.

        Args:
            app_name: Application name for subdirectory

        Returns:
            Path to data directory
        """
        if self.is_windows:
            base = Path(self.get_env('LOCALAPPDATA', ''))
            if not base:
                base = self.get_user_home() / 'AppData' / 'Local'
        elif self.is_macos:
            base = self.get_user_home() / 'Library' / 'Application Support'
        else:  # Linux and others
            base = Path(self.get_env('XDG_DATA_HOME', ''))
            if not base:
                base = self.get_user_home() / '.local' / 'share'

        if app_name:
            base = base / app_name

        return base

    def get_temp_dir(self) -> Path:
        """Get system temporary directory."""
        return Path(self.get_env('TEMP') or self.get_env('TMP') or '/tmp')

    def get_current_working_dir(self) -> Path:
        """Get current working directory."""
        return Path.cwd()

    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return any([
            self.get_env_bool('DEBUG'),
            self.get_env_bool('DEVELOPMENT'),
            self.get_env_bool('DEV'),
            self.get_env('ENVIRONMENT', '').lower() in ('dev', 'development'),
            self.get_env('ENV', '').lower() in ('dev', 'development'),
        ])

    def is_production_mode(self) -> bool:
        """Check if running in production mode."""
        return any([
            self.get_env_bool('PRODUCTION'),
            self.get_env_bool('PROD'),
            self.get_env('ENVIRONMENT', '').lower() in ('prod', 'production'),
            self.get_env('ENV', '').lower() in ('prod', 'production'),
        ])

    def is_testing_mode(self) -> bool:
        """Check if running in testing mode."""
        return any([
            self.get_env_bool('TESTING'),
            self.get_env_bool('TEST'),
            self.get_env('ENVIRONMENT', '').lower() in ('test', 'testing'),
            self.get_env('ENV', '').lower() in ('test', 'testing'),
            'pytest' in sys.modules,
            'unittest' in sys.modules,
        ])

    def get_environment_type(self) -> str:
        """
        Get current environment type.

        Returns:
            Environment type: 'development', 'testing', 'production', or 'unknown'
        """
        if self.is_testing_mode():
            return 'testing'
        elif self.is_development_mode():
            return 'development'
        elif self.is_production_mode():
            return 'production'
        else:
            return 'unknown'

    def get_available_memory_mb(self) -> Optional[float]:
        """
        Get available system memory in MB.

        Returns:
            Available memory in MB or None if cannot determine
        """
        try:
            if self.is_windows:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulong = ctypes.c_ulong
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", c_ulong),
                        ("dwMemoryLoad", c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                memoryStatus = MEMORYSTATUSEX()
                memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
                return memoryStatus.ullAvailPhys / (1024 * 1024)
            else:
                # Unix-like systems
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemAvailable:'):
                            return int(line.split()[1]) / 1024  # Convert KB to MB
                return None
        except Exception:
            return None

    def get_cpu_count(self) -> int:
        """Get number of CPU cores."""
        return os.cpu_count() or 1

    def get_environment_summary(self) -> Dict[str, Any]:
        """Get comprehensive environment summary."""
        return {
            'platform': self.platform_info,
            'python': self.python_info,
            'environment_type': self.get_environment_type(),
            'directories': {
                'home': str(self.get_user_home()),
                'config': str(self.get_user_config_dir()),
                'data': str(self.get_user_data_dir()),
                'temp': str(self.get_temp_dir()),
                'cwd': str(self.get_current_working_dir()),
            },
            'resources': {
                'cpu_count': self.get_cpu_count(),
                'available_memory_mb': self.get_available_memory_mb(),
            },
            'flags': {
                'is_development': self.is_development_mode(),
                'is_production': self.is_production_mode(),
                'is_testing': self.is_testing_mode(),
                'is_64bit': self.is_64bit,
            }
        }


# Global instance for convenience
_env_manager: Optional[EnvironmentManager] = None


def get_environment_manager() -> EnvironmentManager:
    """Get global environment manager instance."""
    global _env_manager
    if _env_manager is None:
        _env_manager = EnvironmentManager()
    return _env_manager
