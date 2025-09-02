from pathlib import Path
from typing import Annotated, Union

import typer

from .commands import branches as _branches
from .commands import check as _check
from .commands import current as _current
from .commands import downgrade as _downgrade
from .commands import edit as _edit
from .commands import heads as _heads
from .commands import history as _history
from .commands import init as _init
from .commands import list_templates as _list_templates
from .commands import merge as _merge
from .commands import migrate as _migrate
from .commands import path_callback
from .commands import revision as _revision
from .commands import show as _show
from .commands import stamp as _stamp
from .commands import upgrade as _upgrade
from .commands import version_callback
from .decorators import ensure_fastapi_rtk_tables_exist

db_app = typer.Typer(rich_markup_mode="rich")


@db_app.callback()
@ensure_fastapi_rtk_tables_exist
def callback(
    version: Annotated[
        Union[bool, None],
        typer.Option(
            "--version", help="Show the version and exit.", callback=version_callback
        ),
    ] = None,
) -> None:
    """
    FastAPI RTK Database CLI - The [bold]fastapi-rtk db[/bold] command line app. 😎

    Manage your [bold]FastAPI React Toolkit[/bold] databases easily with init, migrate, upgrade, with the power of Alembic.
    """


@db_app.command()
def list_templates():
    """List available templates."""
    _list_templates()


@db_app.command()
def init(
    directory: Annotated[
        Union[str, None],
        typer.Option(
            help="A path to a directory where the migration scripts will be stored."
        ),
    ] = "migrations",
    multidb: Annotated[
        bool,
        typer.Option(
            help="Whether multiple databases are being used.",
        ),
    ] = False,
    template: Annotated[
        Union[str, None],
        typer.Option(
            help="Template to use when creating the migration scripts.",
        ),
    ] = "fastapi",
    package: Annotated[
        bool,
        typer.Option(
            help="Whether to include a `__init__.py` file in the migration directory.",
        ),
    ] = False,
):
    """Creates a new migration repository"""
    _init(directory, multidb, template, package)


@db_app.command()
def revision(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    message: Annotated[
        str, typer.Option(help="String message to apply to the revision.")
    ] = "",
    autogenerate: Annotated[
        bool,
        typer.Option(
            help="Whether or not to autogenerate the script from the database."
        ),
    ] = False,
    sql: Annotated[
        bool,
        typer.Option(
            help="Whether to dump the script out as a SQL string; when specified, the script is dumped to stdout."
        ),
    ] = False,
    head: Annotated[
        str,
        typer.Option(help="Head revision to build the new revision upon as a parent."),
    ] = "head",
    splice: Annotated[
        bool,
        typer.Option(
            help="Whether or not the new revision should be made into a new head of its own; is required when the given ``head`` is not itself a head"
        ),
    ] = False,
    branch_label: Annotated[
        Union[str, None],
        typer.Option(
            help="String label to apply to the branch.",
        ),
    ] = None,
    version_path: Annotated[
        Union[str, None],
        typer.Option(
            help="String symbol identifying a specific version path from the configuration.",
        ),
    ] = None,
    rev_id: Annotated[
        Union[str, None],
        typer.Option(
            help="Optional revision identifier to use instead of having one generated.",
        ),
    ] = None,
):
    """Create a new revision file."""
    _revision(
        directory,
        message,
        autogenerate,
        sql,
        head,
        splice,
        branch_label,
        version_path,
        rev_id,
    )


@db_app.command()
def migrate(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    message: Annotated[
        str, typer.Option(help="String message to apply to the revision.")
    ] = "",
    sql: Annotated[
        bool,
        typer.Option(
            help="Whether to dump the script out as a SQL string; when specified, the script is dumped to stdout."
        ),
    ] = False,
    head: Annotated[
        str,
        typer.Option(help="Head revision to build the new revision upon as a parent."),
    ] = "head",
    splice: Annotated[
        bool,
        typer.Option(
            help="Whether or not the new revision should be made into a new head of its own; is required when the given ``head`` is not itself a head"
        ),
    ] = False,
    branch_label: Annotated[
        Union[str, None],
        typer.Option(
            help="String label to apply to the branch.",
        ),
    ] = None,
    version_path: Annotated[
        Union[str, None],
        typer.Option(
            help="String symbol identifying a specific version path from the configuration.",
        ),
    ] = None,
    rev_id: Annotated[
        Union[str, None],
        typer.Option(
            help="Optional revision identifier to use instead of having one generated.",
        ),
    ] = None,
):
    """Alias for `revision` command with --autogenerate."""
    _migrate(
        directory,
        message,
        sql,
        head,
        splice,
        branch_label,
        version_path,
        rev_id,
    )


@db_app.command()
def edit(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    revision: Annotated[
        str, typer.Option(help="Revision identifier to edit.")
    ] = "current",
):
    """Edit the revision."""
    _edit(directory, revision)


@db_app.command()
def merge(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    revisions: Annotated[str, typer.Option(help="Revisions to merge.")] = "",
    message: Annotated[
        Union[str, None], typer.Option(help="String message to apply to the revision.")
    ] = None,
    branch_label: Annotated[
        Union[str, None],
        typer.Option(
            help="String label to apply to the branch.",
        ),
    ] = None,
    rev_id: Annotated[
        Union[str, None],
        typer.Option(
            help="Optional revision identifier to use instead of having one generated.",
        ),
    ] = None,
):
    """Merge two revisions together."""
    _merge(directory, revisions, message, branch_label, rev_id)


@db_app.command()
def upgrade(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    revision: Annotated[
        str, typer.Option(help="Target revision to upgrade to.")
    ] = "head",
    sql: Annotated[
        bool,
        typer.Option(
            help="Whether to dump the script out as a SQL string; when specified, the script is dumped to stdout."
        ),
    ] = False,
    tag: Annotated[
        Union[str, None],
        typer.Option(
            help="Arbitrary 'tag' name to apply to the migration.",
        ),
    ] = None,
):
    """Upgrade to a later version."""
    _upgrade(directory, revision, sql, tag)


@db_app.command()
def downgrade(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    revision: Annotated[
        str, typer.Option(help="Target revision to downgrade to.")
    ] = "-1",
    sql: Annotated[
        bool,
        typer.Option(
            help="Whether to dump the script out as a SQL string; when specified, the script is dumped to stdout."
        ),
    ] = False,
    tag: Annotated[
        Union[str, None],
        typer.Option(
            help="Arbitrary 'tag' name to apply to the migration.",
        ),
    ] = None,
):
    """Downgrade to a previous version."""
    _downgrade(directory, revision, sql, tag)


@db_app.command()
def show(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    revision: Annotated[str, typer.Option(help="Target revision to show.")] = "head",
):
    """Show the revision."""
    _show(directory, revision)


@db_app.command()
def history(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    rev_range: Annotated[
        str, typer.Option(help="Range of revisions to include in the history.")
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            help="Show the full revision message.",
        ),
    ] = False,
    indicate_current: Annotated[
        bool,
        typer.Option(
            help="Indicate the current revision.",
        ),
    ] = False,
):
    """List changeset scripts in chronological order."""
    _history(directory, rev_range, verbose, indicate_current)


@db_app.command()
def heads(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    verbose: Annotated[
        bool,
        typer.Option(
            help="Show the full revision message.",
        ),
    ] = False,
    resolve_dependencies: Annotated[
        bool,
        typer.Option(
            help="Treat dependency version as down revisions.",
        ),
    ] = False,
):
    """Show current available heads in the script directory."""
    _heads(directory, verbose, resolve_dependencies)


@db_app.command()
def branches(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    verbose: Annotated[
        bool,
        typer.Option(
            help="Show the full revision message.",
        ),
    ] = False,
):
    """Show current branch points in the script directory."""
    _branches(directory, verbose)


@db_app.command()
def current(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    verbose: Annotated[
        bool,
        typer.Option(
            help="Show the full revision message.",
        ),
    ] = False,
):
    """Display the current revision for each database."""
    _current(directory, verbose)


@db_app.command()
def stamp(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
    revision: Annotated[str, typer.Option(help="Target revision to stamp.")] = "head",
    sql: Annotated[
        bool,
        typer.Option(
            help="Whether to dump the script out as a SQL string; when specified, the script is dumped to stdout."
        ),
    ] = False,
    tag: Annotated[
        Union[str, None],
        typer.Option(
            help="Arbitrary 'tag' name to apply to the migration.",
        ),
    ] = None,
    purge: Annotated[
        bool,
        typer.Option(
            help="Remove all database tables and then stamp.",
        ),
    ] = False,
):
    """Stamp the revision table with the given revision."""
    _stamp(directory, revision, sql, tag, purge)


@db_app.command()
def check(
    directory: Annotated[
        Union[str, None], typer.Option(help="Path to migration scripts directory.")
    ] = "migrations",
):
    """Check the current revision."""
    _check(directory)
