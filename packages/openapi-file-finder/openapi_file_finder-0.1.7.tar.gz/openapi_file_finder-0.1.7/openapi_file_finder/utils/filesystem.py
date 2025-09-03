"""
Simple filesystem utilities for file enumeration in a repository.

Usage example:
    from openapi_file_finder.utils import filesystem
    for f in filesystem.enumerate_files('/path/to/repo'):
        print(f)
    for f in filesystem.enumerate_files_by_ext('/path/to/repo', 'py'):
        print(f)
    for f in filesystem.enumerate_php_files('/path/to/repo'):
        print(f)
"""
from __future__ import annotations

import os
from collections.abc import Iterator

__all__ = [
    'enumerate_files',
    'enumerate_files_by_ext',
    'enumerate_php_files',
]


def enumerate_files(repository_path: str) -> Iterator[str]:
    """
    Recursively yield all file paths under the given repository path.

    Args:
        repository_path (str): The root directory to search.

    Yields:
        str: Absolute path to each file found.
    """
    for root, _, files in os.walk(repository_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                yield file_path


def enumerate_files_by_ext(root_path: str, ext: str = 'php') -> Iterator[str]:
    """
    Recursively yield all file paths with the given extension under root_path.

    Args:
        root_path (str): The root directory to search.
        ext (str): File extension to filter by (without dot).

    Yields:
        str: Absolute path to each file found with the given extension.
    """
    ext = ext.lstrip('.')
    seen_dirs = set()
    for dirpath, _, filenames in os.walk(root_path, followlinks=False):
        real_path = os.path.realpath(dirpath)
        if real_path in seen_dirs:
            continue
        seen_dirs.add(real_path)
        for filename in filenames:
            if filename.endswith(f".{ext}"):
                yield os.path.join(dirpath, filename)


def enumerate_php_files(root_path: str) -> Iterator[str]:
    """
    Recursively yield all PHP file paths under root_path.

    Args:
        root_path (str): The root directory to search.

    Yields:
        str: Absolute path to each PHP file found.
    """
    return enumerate_files_by_ext(root_path, 'php')
