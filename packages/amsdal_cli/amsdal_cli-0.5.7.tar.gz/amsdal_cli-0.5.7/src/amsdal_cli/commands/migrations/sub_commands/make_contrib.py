import asyncio
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Annotated

import typer
from rich import print as rprint

from amsdal_cli.commands.migrations.app import sub_app
from amsdal_cli.utils.cli_config import ModelsFormat

if TYPE_CHECKING:
    from amsdal_cli.utils.cli_config import CliConfig


def _sync_make_contrib_migrations(
    name: str | None,
    *,
    is_data: bool,
    cli_config: 'CliConfig',
) -> None:
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal.manager import AmsdalManager
    from amsdal_models.migration.data_classes import MigrationFile
    from amsdal_models.migration.file_migration_generator import FileMigrationGenerator
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME
    from amsdal_cli.utils.schema_repository import build_schema_repository
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    amsdal_manager = AmsdalManager()
    if not amsdal_manager._is_setup:
        amsdal_manager.setup()
    amsdal_manager.authenticate()
    amsdal_manager.post_setup()  # type: ignore[call-arg]

    schema_repository = build_schema_repository(cli_config=cli_config)
    migrations_dir: Path = cli_config.app_directory / cli_config.src_dir / MIGRATIONS_DIR_NAME

    generator = FileMigrationGenerator(
        core_migrations_path=CORE_MIGRATIONS_PATH,
        app_migrations_path=migrations_dir,
        contrib_migrations_directory_name=settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
    )

    try:
        name = to_snake_case(name) if name else None
        migration: MigrationFile = generator.make_migrations(
            schemas=schema_repository.contrib_schemas,
            name=name,
            is_data=is_data,
        )
    except UserWarning as warn:
        rprint(rich_info(str(warn)))
    else:
        rprint(rich_success(f'Contrib migration created: {migration.path.name}'))

    try:
        amsdal_manager.teardown()
        AmsdalManager.invalidate()
    except Exception:  # noqa: S110
        pass


async def _async_make_contrib_migrations(
    name: str | None,
    *,
    is_data: bool,
    cli_config: 'CliConfig',
) -> None:
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_models.migration.data_classes import MigrationFile
    from amsdal_models.migration.file_migration_generator import AsyncFileMigrationGenerator
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME
    from amsdal_cli.utils.schema_repository import build_schema_repository
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    amsdal_manager = AsyncAmsdalManager()
    if not amsdal_manager.is_setup:
        await amsdal_manager.setup()
    amsdal_manager.authenticate()
    await amsdal_manager.post_setup()  # type: ignore[call-arg, misc]

    schema_repository = build_schema_repository(cli_config=cli_config)
    migrations_dir: Path = cli_config.app_directory / cli_config.src_dir / MIGRATIONS_DIR_NAME

    generator = AsyncFileMigrationGenerator(
        core_migrations_path=CORE_MIGRATIONS_PATH,
        app_migrations_path=migrations_dir,
        contrib_migrations_directory_name=settings.CONTRIB_MODELS_PACKAGE_NAME,
    )

    try:
        name = to_snake_case(name) if name else None
        migration: MigrationFile = await generator.make_migrations(
            schemas=schema_repository.contrib_schemas,
            name=name,
            is_data=is_data,
        )
    except UserWarning as warn:
        rprint(rich_info(str(warn)))
    else:
        rprint(rich_success(f'Contrib migration created: {migration.path.name}'))

    await amsdal_manager.teardown()
    AsyncAmsdalManager.invalidate()


@sub_app.command(name='new-contrib, nc')
def make_contrib_migrations(
    ctx: typer.Context,
    build_dir: Annotated[Path, typer.Option('--build-dir', '-b')] = Path('.'),
    *,
    name: Annotated[str, typer.Option('--name', '-n', help='Migration name')] = None,  # type: ignore # noqa: RUF013
    is_data: Annotated[bool, typer.Option('--data', '-d', help='Create data migration')] = False,
    config: Annotated[Path, typer.Option('--config', '-c')] = None,  # type: ignore # noqa: RUF013
) -> None:
    """
    Creates schema migration based on the changes in the contrib models' schemas or
    creates an empty data migration using --data flag.

    Example usage:

    1. Automatically creates a schema migrations based on the changes in the contrib models' schemas:
    ```bash
    amsdal migrations new-contrib
    ```

    2. Creates a schema migration with a custom name:
    ```bash
    amsdal migrations new-contrib --name my_custom_contrib_migration
    ```

    3. Creates a data migration:
    ```bash
    amsdal migrations new-contrib --data --name my_contrib_data_migration
    ```
    The data migrations allow you to write a python script to migrate your data. Useful for example when you have added
    a new column to the table and you want to populate it with some data. So you first generate a schema migration that
    adds the column and then you create a data migration that populates the column with the data.
    """
    from amsdal_utils.config.manager import AmsdalConfigManager

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.utils.cli_config import CliConfig

    cli_config: CliConfig = ctx.meta['config']

    app_builder = AppBuilder(
        cli_config=cli_config,
        config_path=config or cli_config.config_path,
    )
    app_builder.build(build_dir, is_silent=True)
    cli_config.models_format = ModelsFormat.PY

    if AmsdalConfigManager().get_config().async_mode:
        asyncio.run(
            _async_make_contrib_migrations(
                name=name,
                is_data=is_data,
                cli_config=cli_config,
            )
        )
    else:
        _sync_make_contrib_migrations(
            name=name,
            is_data=is_data,
            cli_config=cli_config,
        )
