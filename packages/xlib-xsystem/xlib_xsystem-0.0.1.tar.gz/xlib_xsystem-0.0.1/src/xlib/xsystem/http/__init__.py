"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

xSystem HTTP Package

Provides high-performance HTTP client with retry mechanisms, 
connection pooling, and comprehensive error handling.
"""

from .client import HttpClient, HttpError, RetryConfig

__all__ = [
    "HttpClient",
    "HttpError", 
    "RetryConfig",
]
