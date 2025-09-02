"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

xSystem Plugins Package

Provides plugin discovery, registration and management system
with support for entry points and dynamic loading.
"""

from .base import PluginManager, PluginBase, PluginRegistry

__all__ = [
    "PluginManager",
    "PluginBase", 
    "PluginRegistry",
]
