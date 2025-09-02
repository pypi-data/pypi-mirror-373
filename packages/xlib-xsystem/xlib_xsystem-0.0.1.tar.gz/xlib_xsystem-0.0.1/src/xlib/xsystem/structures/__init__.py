"""
Data structure utilities for xsystem.
"""

from .circular_detector import CircularReferenceDetector, CircularReferenceError
from .tree_walker import (
    TreeWalker,
    apply_user_defined_links,
    count_nodes_by_type,
    find_deep_paths,
    resolve_proxies_in_dict,
    walk_and_replace,
)

__all__ = [
    "CircularReferenceDetector",
    "CircularReferenceError",
    "TreeWalker",
    "resolve_proxies_in_dict",
    "apply_user_defined_links",
    "walk_and_replace",
    "count_nodes_by_type",
    "find_deep_paths",
]
