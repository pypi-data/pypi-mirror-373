import shutil
import tempfile
import typing
from pathlib import Path
from typing import Union

import amsdal_glue as glue
import typer
import yaml
from amsdal_data.connections.db_alias_map import CONNECTION_BACKEND_ALIASES
from rich import print as rprint
from typer import Option

from amsdal_cli.commands.cloud.app import cloud_sub_app
from amsdal_cli.commands.cloud.enums import DBType

if typing.TYPE_CHECKING:
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_utils.config.data_models.amsdal_config import AmsdalConfig

    from amsdal_cli.utils.cli_config import CliConfig


@cloud_sub_app.command(name='sync-db, sync_db, sdb')
def sync_db_command(
    ctx: typer.Context,
    env_name: typing.Annotated[
        typing.Optional[str],  # noqa: UP007
        Option('--env', help='Environment name. Default is the current environment from configuration.'),
    ] = None,
    db_type: DBType = DBType.sqlite,
    *,
    skip_expose_db: bool = typer.Option(False, '-s', help='Skip exposing the database'),
    skip_copy_data: bool = typer.Option(False, '-c', help='Skip copying data'),
    skip_state_db: bool = typer.Option(False, '-skip-state', help='Skip sync state db'),
    skip_lakehouse_db: bool = typer.Option(False, '-skip-lakehouse', help='Skip sync lakehouse db'),
) -> None:
    """
    Recreate local database from the remote one.

    Args:
        ctx (typer.Context): The Typer context object.
        env_name (typing.Annotated[typing.Optional[str], Option]): The name of the environment. Defaults to the current
            environment from configuration.
        db_type (DBType): The type of the database. Defaults to DBType.sqlite.
        skip_expose_db (bool): Whether to skip exposing the database. Defaults to False.
        skip_copy_data (bool): Whether to skip copying data. Defaults to False.
        skip_state_db (bool): Whether to skip syncing state db. Defaults to False.
        skip_lakehouse_db (bool): Whether to skip syncing lakehouse db. Defaults to False.

    Returns:
        None
    """
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_utils.config.manager import AmsdalConfigManager
    from amsdal_utils.utils.singleton import Singleton

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.commands.cloud.environments.utils import get_current_env
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.text import rich_highlight
    from amsdal_cli.utils.text import rich_info

    cli_config: CliConfig = ctx.meta['config']
    env_name = env_name or get_current_env(cli_config)

    if cli_config.verbose:
        rprint(rich_info(f'Syncing database for environment: {rich_highlight(env_name)}'))

    config_path: Path
    if not skip_expose_db:
        with tempfile.TemporaryDirectory() as _temp_dir:
            output_path: Path = Path(_temp_dir)

            app_builder = AppBuilder(
                cli_config=cli_config,
                config_path=cli_config.config_path,
            )

            app_builder.build(output_path, is_silent=True)
            manager: AsyncAmsdalManager | AmsdalManager

            if AmsdalConfigManager().get_config().async_mode:
                manager = AsyncAmsdalManager()
            else:
                manager = AmsdalManager()

            manager.pre_setup()
            manager.authenticate()

        creds: dict[str, str] = _load_credentials(manager, cli_config, env_name)
        _expose_db(manager, cli_config, env_name)

        Singleton.invalidate(Singleton)  # type: ignore[arg-type]
        config_path = _build_config(creds, db_type)
    else:
        config_path = Path('sync-config.yml')

    if skip_copy_data:
        rprint(rich_info('Skip copy data flag is set. Skipping data copy.'))
        return

    if db_type == DBType.sqlite and Path('warehouse').exists():
        shutil.rmtree(str(Path('warehouse').resolve()))

    config_manager = AmsdalConfigManager()
    config_manager.load_config(config_path)

    connection_names = []

    if not skip_lakehouse_db:
        connection_names.append(('remote_historical', 'local_historical'))
    if not skip_state_db:
        connection_names.append(('remote_state', 'local_state'))

    _copy_data(config_manager.get_config(), connection_names=connection_names)


def _load_credentials(
    manager: Union['AmsdalManager', 'AsyncAmsdalManager'], cli_config: 'CliConfig', env_name: str
) -> dict[str, str]:
    from amsdal.errors import AmsdalCloudError

    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    rprint(rich_info('Receiving credentials... '), end='')

    try:
        list_response = manager.cloud_actions_manager.list_secrets(
            with_values=True,
            env_name=env_name,
            application_uuid=cli_config.application_uuid,
            application_name=cli_config.application_name,
        )
    except AmsdalCloudError as e:
        rprint(rich_error(str(e)))
        raise typer.Exit(1) from e

    secrets = {}

    if list_response.secrets:
        for secret in list_response.secrets:
            secret_name, secret_value = secret.split('=', 1)
            secrets[secret_name] = secret_value

    rprint(rich_success('OK'))

    return secrets


def _expose_db(manager: Union['AmsdalManager', 'AsyncAmsdalManager'], cli_config: 'CliConfig', env_name: str) -> None:
    from amsdal.errors import AmsdalCloudError

    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    rprint(rich_info('Exposing database...'), end='')
    try:
        manager.cloud_actions_manager.expose_db(
            env_name=env_name,
            application_uuid=cli_config.application_uuid,
            application_name=cli_config.application_name,
            ip_address=None,
        )
    except AmsdalCloudError as e:
        rprint(rich_error(str(e)))
        raise typer.Exit(1) from e

    rprint(rich_success('OK'))


def _build_config(secrets: dict[str, str], db_type: DBType) -> Path:
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    rprint(rich_info('Building config...'), end='')

    with open('config.yml') as _f:
        _origin_config = yaml.safe_load(_f)

    _config: Path = Path('sync-config.yml')
    _dns_historical = f'postgresql://{secrets["POSTGRES_USER"]}:{secrets["POSTGRES_PASSWORD"]}@{secrets["POSTGRES_HOST"]}:{secrets["POSTGRES_PORT"]}/{secrets["POSTGRES_DATABASE"]}'
    _dns_state = f'postgresql://{secrets["POSTGRES_STATE_USER"]}:{secrets["POSTGRES_STATE_PASSWORD"]}@{secrets["POSTGRES_STATE_HOST"]}:{secrets["POSTGRES_STATE_PORT"]}/{secrets["POSTGRES_STATE_DATABASE"]}'
    sqlite_history_db_path = './warehouse/amsdal_historical.sqlite3'
    sqlite_state_db_path = './warehouse/amsdal_state.sqlite3'

    if db_type == DBType.sqlite:
        for conn in _origin_config['connections']:
            if conn['name'] == _origin_config['resources_config']['lakehouse']:
                sqlite_history_db_path = conn['credentials'][0]['db_path']
            elif conn['backend'] == _origin_config['resources_config']['repository']['default']:
                sqlite_state_db_path = conn['credentials'][0]['db_path']

    _config_template = SQLITE_CONFIG_TMPL if db_type == DBType.sqlite else POSTGRES_CONFIG_TMPL
    _config_content = (
        _config_template.replace('{{app_name}}', _origin_config['application_name'])
        .replace('{{dns_historical}}', _dns_historical)
        .replace('{{dns_state}}', _dns_state)
        .replace('{{sqlite_history_db_path}}', sqlite_history_db_path)
        .replace('{{sqlite_state_db_path}}', sqlite_state_db_path)
        .strip()
    )
    _config.write_text(_config_content)
    rprint(rich_success('OK'))

    return _config


def _copy_data(config: 'AmsdalConfig', connection_names: list[tuple[str, str]]) -> None:
    from amsdal_utils.utils.classes import import_class

    for from_name, to_name in connection_names:
        from_creds = config.connections[from_name].credentials
        from_backend_alias = config.connections[from_name].backend
        from_backend = import_class(CONNECTION_BACKEND_ALIASES.get(from_backend_alias, from_backend_alias))
        to_creds = config.connections[to_name].credentials
        to_backend_alias = config.connections[to_name].backend
        to_backend = import_class(CONNECTION_BACKEND_ALIASES.get(to_backend_alias, to_backend_alias))

        from_connection = from_backend()
        from_connection.connect(**from_creds)
        to_connection = to_backend()
        to_connection.connect(**to_creds)

        for schema in from_connection.query_schema():
            to_connection.run_schema_command(
                glue.SchemaCommand(
                    mutations=[
                        glue.RegisterSchema(schema=schema),
                    ],
                ),
            )
            _query = glue.QueryStatement(
                table=glue.SchemaReference(
                    name=schema.name,
                    version=glue.Version.LATEST,
                ),
            )

            for data in from_connection.query(_query):
                to_connection.run_mutations(
                    mutations=[
                        glue.InsertData(
                            schema=glue.SchemaReference(
                                name=schema.name,
                                version=glue.Version.LATEST,
                            ),
                            data=[data],
                        ),
                    ],
                )


SQLITE_CONFIG_TMPL = """
application_name: {{app_name}}
connections:
  - name: local_historical
    backend: sqlite-state
    credentials:
      - db_path: {{sqlite_history_db_path}}
      - check_same_thread: false
  - name: local_state
    backend: sqlite-state
    credentials:
      - db_path: {{sqlite_state_db_path}}
      - check_same_thread: false
  - name: remote_historical
    backend: postgres-state
    credentials:
      dsn: {{dns_historical}}
  - name: remote_state
    backend: postgres-state
    credentials:
      dsn: {{dns_state}}
  - name: lock
    backend: amsdal_data.lock.implementations.thread_lock.ThreadLock
resources_config:
  lakehouse: local_historical
  lock: lock
  repository:
    default: local_state
"""

POSTGRES_CONFIG_TMPL = """
application_name: {{app_name}}
connections:
  - name: local_historical
    backend: postgres-state
    credentials:
      - dsn: postgresql://postgres:mysecretpassword@localhost:5432/amsdal_historical
  - name: local_state
    backend: postgres-state
    credentials:
      - dsn: postgresql://postgres:mysecretpassword@localhost:5432/amsdal_state
  - name: remote_historical
    backend: postgres-state
    credentials:
      dsn: {{dns_historical}}
  - name: remote_state
    backend: postgres-state
    credentials:
      dsn: {{dns_state}}
  - name: lock
    backend: amsdal_data.lock.implementations.thread_lock.ThreadLock
resources_config:
  lakehouse: local_historical
  lock: lock
  repository:
    default: local_state
"""
