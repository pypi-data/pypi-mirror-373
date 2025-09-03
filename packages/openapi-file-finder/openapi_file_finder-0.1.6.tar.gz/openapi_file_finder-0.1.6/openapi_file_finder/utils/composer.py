from __future__ import annotations

import json
import os


def _read_composer_json(path: str) -> dict | None:
    """
    Read and parse composer.json file.

    Args:
            path: Path to the composer.json file

    Returns:
            Parsed JSON content as dict, or None if file cannot be read/parsed
    """
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _has_dependency(composer_data: dict, package_name: str) -> bool:
    """Return True if package exists in require or require-dev."""
    require = composer_data.get('require') or {}
    require_dev = composer_data.get('require-dev') or {}
    return package_name in require or package_name in require_dev


def has_dedoc_scramble_dependency(composer_json_path: str) -> bool:
    """
    Check if composer.json contains dedoc/scramble dependency.

    Args:
            composer_json_path: Path to the composer.json file

    Returns:
            True if dedoc/scramble is found in require or require-dev sections
    """
    return has_specific_dependency(composer_json_path, 'dedoc/scramble')


def find_composer_json_files(repo_path: str, max_depth: int = 6) -> list[str]:
    """
    Find all composer.json files in the repository.

    Args:
            repo_path: Root path of the repository
            max_depth: Maximum directory depth to search

    Returns:
            List of full paths to composer.json files
    """
    composer_files = []
    for root, _, files in os.walk(repo_path):
        if 'composer.json' in files:
            full_path = os.path.join(root, 'composer.json')
            rel_path = os.path.relpath(full_path, repo_path)
            # Check depth limit
            if rel_path.count(os.sep) > max_depth:
                continue
            composer_files.append(full_path)
    return composer_files


def has_specific_dependency(composer_json_path: str, package_name: str) -> bool:
    """Generic checker for any composer package dependency in require/require-dev."""
    if not os.path.isfile(composer_json_path):
        return False
    composer_data = _read_composer_json(composer_json_path)
    if not composer_data:
        return False
    return _has_dependency(composer_data, package_name)


def check_specific_dependency_in_repo(repo_path: str, package_name: str) -> bool:
    """Generic repo-wide checker for a composer package."""
    composer_files = find_composer_json_files(repo_path)
    for composer_file in composer_files:
        if has_specific_dependency(composer_file, package_name):
            return True
    return False


def check_scramble_dependency_in_repo(repo_path: str) -> bool:
    """Check if dedoc/scramble dependency is used in composer.json files."""
    return check_specific_dependency_in_repo(repo_path, 'dedoc/scramble')


def check_scribe_dependency_in_repo(repo_path: str) -> bool:
    """Check if knuckleswtf/scribe dependency is used in composer.json files."""
    return check_specific_dependency_in_repo(repo_path, 'knuckleswtf/scribe')


def check_swagger_php_dependency_in_repo(repo_path: str) -> bool:
    """Check if zircote/swagger-php dependency is used in composer.json files."""
    return check_specific_dependency_in_repo(repo_path, 'zircote/swagger-php')


def check_apiblueprint_dependency_in_repo(repo_path: str) -> bool:
    """Check if dingo/blueprint dependency is used in composer.json files."""
    return check_specific_dependency_in_repo(repo_path, 'dingo/blueprint')
