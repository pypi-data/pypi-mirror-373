from __future__ import annotations

import json
import os
from collections.abc import Callable

import yaml

from openapi_file_finder.config import OPENAPI_SPEC_PATTERN


def _read_file(path: str, mode: str = 'r', encoding: str = 'utf-8') -> bytes:
    try:
        with open(path, mode, encoding=encoding if 'b' not in mode else None) as f:
            content = f.read()
            return content.encode('utf-8') if isinstance(content, str) else content
    except Exception:
        return b''


def _find_candidate_spec_files(repo_path: str, exclude_keywords: list[str] = ['test'], max_depth: int = 6) -> list[str]:
    candidates = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if OPENAPI_SPEC_PATTERN.match(file):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_path)
                if any(keyword in rel_path.lower() for keyword in exclude_keywords):
                    continue
                if rel_path.count(os.sep) > max_depth:
                    continue
                candidates.append(full_path)
    return candidates


def _is_valid_openapi_content(content: bytes, file_path: str) -> bool:
    if not content:
        return False
    if b'swagger' not in content.lower() and b'openapi' not in content.lower():
        return False
    if file_path.endswith(('.yaml', '.yml')):
        try:
            spec = yaml.safe_load(content)
        except Exception:
            return False
    elif file_path.endswith('.json'):
        try:
            spec = json.loads(content)
        except Exception:
            return False
    else:
        return False
    return isinstance(spec, dict) and ('swagger' in spec or 'openapi' in spec) and 'paths' in spec


def _is_valid_openapi_file(file_path: str) -> bool:
    content = _read_file(file_path)
    return _is_valid_openapi_content(content, file_path)


def _find_and_validate_spec_files(repo_path: str, is_valid_func: Callable[[str], bool]) -> list[str]:
    candidates = _find_candidate_spec_files(repo_path)
    return [os.path.relpath(f, repo_path) for f in candidates if is_valid_func(f)]


def find_and_validate_openapi_files(repo_path: str) -> list[str]:
    """
    Return a list of relative paths to valid Swagger/OpenAPI spec files in the repo.
    """
    return _find_and_validate_spec_files(repo_path, _is_valid_openapi_file)


def find_and_validate_openapi_file(repo_path: str) -> str | None:
    """
    Return the openapi file path with the largest file size from the given file path's directory.
    """
    openapi_files = find_and_validate_openapi_files(repo_path)
    if not openapi_files:
        return None
    max_file = max(
        openapi_files, key=lambda f: os.path.getsize(
            os.path.join(repo_path, f),
        ),
    )
    return max_file
