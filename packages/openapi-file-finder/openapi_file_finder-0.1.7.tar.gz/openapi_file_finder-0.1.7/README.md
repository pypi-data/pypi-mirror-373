# openapi-file-finder

A CLI tool and Python package to detect and locate OpenAPI/Swagger and API Blueprint specification files or annotations in PHP repositories.

## Features
- Scan repositories for OpenAPI/Swagger YAML/JSON files
- Detect swagger-php and API Blueprint annotations in PHP code
- Synchronous and asynchronous scanning
- Rich CLI output with logging

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. To install dependencies:

```bash
uv pip install -e .
```

## CLI Usage

```bash
python -m openapi_file_finder find /path/to/php/repository
python -m openapi_file_finder check-swagger-php /path/to/php/repository
python -m openapi_file_finder check-apiblueprint /path/to/php/repository
```

## As a Python Package

You can also use the core functions in your own Python scripts. See `example_usage.py` below.

## Logging

All scripts use `structlog` for structured logging.

## License

MIT
