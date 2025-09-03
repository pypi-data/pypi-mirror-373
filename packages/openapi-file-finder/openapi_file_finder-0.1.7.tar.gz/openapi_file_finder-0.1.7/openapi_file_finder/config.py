from __future__ import annotations

import re

OPENAPI_SPEC_PATTERN = re.compile(
    r'.*(swagger|api).*\.(yaml|yml|json)$', re.IGNORECASE,
)
SWAGGER_PHP_PATTERNS = [b'#[OA\\', b'@OA\\', b'OpenApi']
APIBLUEPRINT_PATTERNS = [b'@Parameters(']
