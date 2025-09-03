from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from openapi_file_finder.utils.validate import find_and_validate_openapi_file
from openapi_file_finder.utils.validate import find_and_validate_openapi_files

console = Console()


def find(
    repo_path: str = typer.Argument(
        ...,
        help='Path to the repository to scan',
    ),
):
    """
    Find and validate OpenAPI/Swagger specification files in the repository.
    """
    import structlog
    logger = structlog.get_logger()
    files = find_and_validate_openapi_files(repo_path)
    if files:
        table = Table(title='OpenAPI/Swagger Specification Files')
        table.add_column('File Path', style='cyan')
        for f in files:
            table.add_row(f)
        console.print(table)
        logger.info('found_openapi_files', count=len(files))
    else:
        console.print(
            '[bold red]No valid OpenAPI/Swagger specification files found.[/bold red]',
        )
        logger.warning('no_openapi_files_found')


def largest(
    file_path: str = typer.Argument(
        ..., help='Specify a file path to find the largest OpenAPI file in the same directory',
    ),
):
    """
    Find the largest OpenAPI file in the same directory as the specified file.
    """
    import structlog
    logger = structlog.get_logger()
    result = find_and_validate_openapi_file(file_path)
    if result:
        console.print(
            f"[bold green]Largest OpenAPI file found: {result}[/bold green]",
        )
        logger.info('max_openapi_file_found', file=result)
    else:
        console.print('[bold red]No valid OpenAPI file found.[/bold red]')
        logger.warning('no_openapi_file_found')


def list_composer_files(
    repo_path: str = typer.Argument(
        ...,
        help='Path to the repository to scan',
    ),
):
    """
    Check if dedoc/scramble dependency is used in composer.json files.
    """
    from openapi_file_finder.utils.composer import find_composer_json_files
    files = find_composer_json_files(repo_path)
    if files:
        table = Table(title='Composer Files')
        table.add_column('File Path', style='cyan')
        for f in files:
            table.add_row(f)
        console.print(table)
    else:
        console.print('[bold red]No composer.json files found.[/bold red]')
