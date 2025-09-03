from pathlib import Path
from typing import Annotated

import typer

from amsdal_cli.commands.migrations.app import sub_app
from amsdal_cli.commands.migrations.sub_commands.apply import apply_migrations
from amsdal_cli.commands.migrations.sub_commands.list import list_migrations
from amsdal_cli.commands.migrations.sub_commands.make import make_migrations
from amsdal_cli.commands.migrations.sub_commands.make_contrib import make_contrib_migrations

__all__ = [
    'apply_migrations',
    'list_migrations',
    'make_contrib_migrations',
    'make_migrations',
]


@sub_app.callback(invoke_without_command=True)
def migrations_list_callback(
    ctx: typer.Context,
    build_dir: Annotated[Path, typer.Option('--build-dir', '-b')] = Path('.'),
    *,
    config: Annotated[Path, typer.Option('--config', '-c')] = None,  # type: ignore # noqa: RUF013
) -> None:
    """
    Show all migrations, which are applied and not applied including CORE and CONTRIB migrations.
    """

    if ctx.invoked_subcommand is not None:
        return

    list_migrations(ctx, build_dir=build_dir, config=config)
