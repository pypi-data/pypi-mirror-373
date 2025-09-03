from __future__ import annotations

import os

from openapi_file_finder.config import APIBLUEPRINT_PATTERNS
from openapi_file_finder.config import SWAGGER_PHP_PATTERNS
from openapi_file_finder.utils.filesystem import enumerate_php_files


def _read_file(path: str, mode: str = 'r') -> bytes:
    try:
        with open(path, mode) as f:
            return f.read()
    except Exception:
        return b''


def _file_contains_any_pattern(path: str, patterns: list[bytes]) -> bool:
    if not os.path.isfile(path):
        return False
    content = _read_file(path, mode='rb')
    if content is None:
        return False
    return any(p in content for p in patterns)


def _check_repository_pattern_usage(repository_path: str, patterns: list[bytes]) -> bool:
    for php_file in enumerate_php_files(repository_path):
        if _file_contains_any_pattern(php_file, patterns):
            return True
    return False


def check_repository_swagger_php_code_snippet_usage(repository_path: str) -> bool:
    """
    Return True if any PHP file in the repo uses swagger-php annotations.
    """
    return _check_repository_pattern_usage(repository_path, SWAGGER_PHP_PATTERNS)


def check_repository_apiblueprint_code_snippet_usage(repository_path: str) -> bool:
    """
    Return True if any PHP file in the repo uses API Blueprint annotations.
    """
    return _check_repository_pattern_usage(repository_path, APIBLUEPRINT_PATTERNS)
