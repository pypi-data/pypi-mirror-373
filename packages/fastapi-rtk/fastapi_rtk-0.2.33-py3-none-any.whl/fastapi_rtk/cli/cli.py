from pathlib import Path
from typing import Annotated, Union

import typer

from .commands import path_callback, version_callback
from .db import db_app
from .export import export_app
from .security import security_app

app = typer.Typer(rich_markup_mode="rich")

app.add_typer(db_app, name="db")
app.add_typer(security_app, name="security")
app.add_typer(export_app, name="export")


@app.callback()
def callback(
    version: Annotated[
        Union[bool, None],
        typer.Option(
            "--version", help="Show the version and exit.", callback=version_callback
        ),
    ] = None,
    path: Annotated[
        Union[Path, None],
        typer.Option(
            help="A path to a Python file or package directory (with [blue]__init__.py[/blue] files) containing a [bold]FastAPI[/bold] app. If not provided, a default set of paths will be tried.",
            callback=path_callback,
        ),
    ] = None,
) -> None:
    """
    FastAPI RTK CLI - The [bold]fastapi-rtk[/bold] command line app. 😎

    Manage your [bold]FastAPI React Toolkit[/bold] projects.
    """


def main():
    app()
