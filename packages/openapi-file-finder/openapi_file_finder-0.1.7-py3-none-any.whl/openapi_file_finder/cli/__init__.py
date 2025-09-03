from __future__ import annotations

import typer

from .check import check_apiblueprint_code_snippet
from .check import check_composer_apiblueprint
from .check import check_composer_scramble
from .check import check_composer_swagger_php
from .check import check_swagger_php_code_snippet
from .find import find
from .find import largest
from .find import list_composer_files

app = typer.Typer()
app.command()(find)
app.command()(largest)
app.command()(list_composer_files)
app.command()(check_swagger_php_code_snippet)
app.command()(check_apiblueprint_code_snippet)
app.command()(check_composer_scramble)
app.command()(check_composer_swagger_php)
app.command()(check_composer_apiblueprint)
