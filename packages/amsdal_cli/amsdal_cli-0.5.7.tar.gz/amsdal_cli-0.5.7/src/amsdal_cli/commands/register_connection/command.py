import asyncio
import tempfile
from pathlib import Path
from typing import Annotated

import typer

from amsdal_cli.app import app
from amsdal_cli.commands.cloud.enums import DBType
from amsdal_cli.commands.register_connection.utils.config_updater import ConfigUpdater
from amsdal_cli.commands.register_connection.utils.credentials import process_credentials
from amsdal_cli.commands.register_connection.utils.meta import process_meta
from amsdal_cli.commands.register_connection.utils.migrate_models import migrate_models_to_lakehouse
from amsdal_cli.commands.register_connection.utils.model_generator import ModelGenerator


@app.command(name='register-connection, reg-conn')
def register_connection_command(
    ctx: typer.Context,
    db_type: DBType,
    credentials: Annotated[
        list[str],
        typer.Option(
            ...,
            '-creds',
            help='Credentials for the connection in the format: prop="value". The `prop=1.0` format is also supported '
            'and will be converted to a float. To get a boolean, use `prop=true` or `prop=false`. To get a Path '
            'use `prop="path/to/file"::path`.',
        ),
    ],
    *,
    meta: Annotated[
        list[str] | None,
        typer.Option(
            ...,
            '-meta',
            help='Metadata for the connection. Useful to specify primary keys, foreign keys, etc. The format is '
            'the next: pk="file_name.csv:column1,column2"',
        ),
    ] = None,
    connection_name: Annotated[
        str | None,
        typer.Option(help='Name of the connection to be registered. If not provided, it will be generated.'),
    ] = None,
    backend: Annotated[
        str | None,
        typer.Option(
            help="Backend to use for the connection. If it's not provided, it will be resolved from db_type.",
        ),
    ] = None,
    config: Annotated[Path | None, typer.Option(help='Path to custom config.yml file')] = None,
) -> None:
    """
    Registers and adds a new connection to the AMSDAL configuration.

    Example of usage:

    1. Register a connection to a SQLite database:
    ```bash
    amsdal reg-conn sqlite -creds db_path=path/to/file/db.sqlite3
    ```
    2. Register a connection to a PostgreSQL database:
    ```bash
    amsdal reg-conn postgres -creds dsn='postgresql://user:password@localhost:5432/mydatabase' -creds schema=public
    ```

    3. Register a connection to a CSV file:
    ```bash
    amsdal reg-conn csv -creds db_path=src/csv_dir/ -meta pk="data.csv:column_name"
    ```

    Register existing connection flow:

    1. First of all, make sure the core migrations are applied and you have initialized lakehouse and default state
       db using `amsdal migrations apply`
    2. Run `amsdal reg-conn` command to register a new connection, e.g. `amsdal reg-conn sqlite -creds
       db_path=external_db.sqlite3`
    3. The connection was added to your config. Data from external connection was synced with lakehouse. The models were
       generated.
    4. Now you need to generate migrations for the new models. Run `amsdal migrations new` to generate migrations for
       the new models.
    5. The last step is to apply the new migrations in fake mode. Run `amsdal migrations apply --fake` to apply the new
       migrations.
    """
    asyncio.run(
        _register_connection_command(
            ctx,
            db_type,
            credentials,
            meta=meta,
            connection_name=connection_name,
            backend=backend,
            config=config,
        )
    )


async def _register_connection_command(
    ctx: typer.Context,
    db_type: DBType,
    credentials: list[str],
    *,
    meta: list[str] | None,
    connection_name: str | None,
    backend: str | None,
    config: Path | None,
) -> None:
    from amsdal_cli.commands.register_connection.utils.initialize import init_amsdal
    from amsdal_cli.commands.register_connection.utils.tables import fetch_tables
    from amsdal_cli.utils.cli_config import CliConfig

    cli_config: CliConfig = ctx.meta['config']

    _creds = process_credentials(credentials)
    _meta = process_meta(meta)
    _config = config or cli_config.config_path

    with ConfigUpdater(_config) as updater:
        _connection_name, _ = updater.add_connection(db_type, connection_name, backend, _creds)

    with tempfile.TemporaryDirectory() as _temp_dir:
        temp_dir = Path(_temp_dir)
        await init_amsdal(_config, temp_dir)

        models = await fetch_tables(_connection_name)

    if not models:
        typer.echo('No tables found for the connection.')
        return

    with ConfigUpdater(_config) as updater:
        updater.link_connection_to_models(_connection_name, models)

    generator = ModelGenerator(
        config_path=_config,
        meta=_meta,
        output_dir=cli_config.app_directory / cli_config.src_dir / 'models',
        models_format=cli_config.models_format,
    )

    generator.generate(_connection_name, cli_config=cli_config)

    await migrate_models_to_lakehouse(_connection_name, cli_config, _config)
