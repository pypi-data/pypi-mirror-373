#!/usr/bin/env python3
"""
Path utilities for xSystem.
Provides common path operations and project root detection.
"""

import os
from pathlib import Path
from typing import Optional


def get_project_root(from_file: Optional[str] = None, levels_up: int = 7) -> Path:
    """
    Get the project root directory.

    Args:
        from_file: The file path to start from (defaults to __file__)
        levels_up: Number of parent directories to traverse (default: 7 for xnode tests)

    Returns:
        Path to the project root directory

    Raises:
        FileNotFoundError: If the project root cannot be found
    """
    if from_file is None:
        # Try to get the calling file
        import inspect

        frame = inspect.currentframe()
        try:
            while frame and frame.f_back:
                frame = frame.f_back
                if frame.f_code.co_filename != __file__:
                    from_file = frame.f_code.co_filename
                    break
        finally:
            del frame

    if from_file is None:
        # Fallback to current working directory
        from_file = os.getcwd()

    current_path = Path(from_file).resolve()

    # If it's a file, start from its parent directory
    if current_path.is_file():
        current_path = current_path.parent

    # Traverse up the specified number of levels
    for _ in range(levels_up):
        current_path = current_path.parent
        if not current_path.exists():
            raise FileNotFoundError(
                f"Project root not found after traversing {levels_up} levels up from {from_file}"
            )

    return current_path


def get_src_path(from_file: Optional[str] = None, levels_up: int = 7) -> Path:
    """
    Get the src directory path within the project.

    Args:
        from_file: The file path to start from (defaults to __file__)
        levels_up: Number of parent directories to traverse (default: 7 for xnode tests)

    Returns:
        Path to the src directory

    Raises:
        FileNotFoundError: If the src directory cannot be found
    """
    project_root = get_project_root(from_file, levels_up)
    src_path = project_root / "src"

    if not src_path.exists():
        raise FileNotFoundError(f"src directory not found at {src_path}")

    return src_path


def setup_python_path(
    from_file: Optional[str] = None, levels_up: int = 7
) -> tuple[Path, Path]:
    """
    Setup Python path by adding src directory to sys.path.

    Args:
        from_file: The file path to start from (defaults to __file__)
        levels_up: Number of parent directories to traverse (default: 7 for xnode tests)

    Returns:
        Tuple of (project_root, src_path)
    """
    import sys

    project_root = get_project_root(from_file, levels_up)
    src_path = get_src_path(from_file, levels_up)

    # Add src to Python path if not already there
    src_path_str = str(src_path)
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)

    return project_root, src_path
