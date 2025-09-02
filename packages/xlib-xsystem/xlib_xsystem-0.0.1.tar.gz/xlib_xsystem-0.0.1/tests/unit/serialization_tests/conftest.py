"""
Configuration and fixtures for serialization tests.
"""

import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_data():
    """Standard test data for serialization tests."""
    return {
        "name": "Test User",
        "age": 30,
        "active": True,
        "scores": [85, 92, 78],
        "metadata": {
            "created": "2025-01-31",
            "tags": ["test", "sample"]
        }
    }

@pytest.fixture
def simple_data():
    """Simple test data for basic serialization tests."""
    return {"x": 1, "y": "test", "z": True}

@pytest.fixture
def csv_data():
    """Data suitable for CSV testing."""
    return [
        {"name": "Alice", "age": 25, "city": "NYC"},
        {"name": "Bob", "age": 30, "city": "LA"},
        {"name": "Charlie", "age": 35, "city": "Chicago"}
    ]

@pytest.fixture
def binary_data():
    """Binary data for testing binary formats."""
    return b"This is binary test data \x00\x01\x02"

@pytest.fixture
def multipart_data():
    """Data suitable for multipart testing."""
    return {
        "text_field": "Hello World",
        "number_field": "42",
        "file_field": {
            "content": b"File content here",
            "filename": "test.txt",
            "content_type": "text/plain"
        }
    }
