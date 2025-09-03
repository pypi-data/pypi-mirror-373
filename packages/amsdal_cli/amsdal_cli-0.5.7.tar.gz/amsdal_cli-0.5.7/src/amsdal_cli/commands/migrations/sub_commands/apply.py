import asyncio
from pathlib import Path
from typing import Annotated

import typer
from amsdal_utils.models.enums import ModuleType
from rich import print as rprint

from amsdal_cli.commands.migrations.app import sub_app
from amsdal_cli.commands.migrations.utils import render_migrations_list


def _sync_apply(
    number: str | None,
    build_dir: Path,
    *,
    module_type: ModuleType,
    fake: bool,
) -> None:
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal.manager import AmsdalManager
    from amsdal_models.migration.data_classes import MigrationDirection
    from amsdal_models.migration.data_classes import MigrationResult
    from amsdal_models.migration.executors.default_executor import DefaultMigrationExecutor
    from amsdal_models.migration.file_migration_executor import FileMigrationExecutorManager
    from amsdal_models.migration.migrations import MigrationSchemas
    from amsdal_models.migration.migrations_loader import MigrationsLoader
    from amsdal_models.migration.utils import build_migrations_module_name

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success
    from amsdal_cli.utils.text import rich_warning

    amsdal_manager = AmsdalManager()

    if not amsdal_manager._is_setup:
        amsdal_manager.setup()

    amsdal_manager.authenticate()
    amsdal_manager.post_setup()  # type: ignore[call-arg]

    app_migrations_loader = MigrationsLoader(
        migrations_dir=build_dir / MIGRATIONS_DIR_NAME,
        module_type=ModuleType.USER,
        module_name=build_migrations_module_name(
            None,
            MIGRATIONS_DIR_NAME,
        ),
    )
    schemas = MigrationSchemas()

    executor = FileMigrationExecutorManager(
        core_migrations_path=CORE_MIGRATIONS_PATH,
        app_migrations_loader=app_migrations_loader,
        executor=DefaultMigrationExecutor(schemas),
        contrib=settings.CONTRIBS,
        contrib_migrations_directory_name=settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
    )

    if number and number.lower().strip() == 'zero':
        number = '-1'

    result: list[MigrationResult] = executor.execute(
        migration_number=int(number) if number else None,
        module_type=module_type,
        fake=fake,
    )

    if not result:
        rprint(rich_info('Migrations are up to date'))
        return

    reverted = [item for item in result if item.direction == MigrationDirection.BACKWARD]
    applied = [item for item in result if item.direction == MigrationDirection.FORWARD]

    if reverted:
        rprint(rich_warning('Migrations reverted'))
        render_migrations_list([item.migration for item in reverted], color='yellow', is_migrated=False)

    if applied:
        rprint(rich_success('Migrations applied'))
        render_migrations_list([item.migration for item in applied], color='green', is_migrated=True)

    amsdal_manager.teardown()


async def _async_sync_apply(
    number: str | None,
    build_dir: Path,
    *,
    module_type: ModuleType,
    fake: bool,
) -> None:
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_models.migration.data_classes import MigrationDirection
    from amsdal_models.migration.data_classes import MigrationResult
    from amsdal_models.migration.executors.default_executor import DefaultAsyncMigrationExecutor
    from amsdal_models.migration.file_migration_executor import AsyncFileMigrationExecutorManager
    from amsdal_models.migration.migrations import MigrationSchemas
    from amsdal_models.migration.migrations_loader import MigrationsLoader
    from amsdal_models.migration.utils import build_migrations_module_name

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success
    from amsdal_cli.utils.text import rich_warning

    amsdal_manager = AsyncAmsdalManager()
    if not amsdal_manager.is_setup:
        await amsdal_manager.setup()

    try:
        amsdal_manager.authenticate()

        await amsdal_manager.post_setup()  # type: ignore[call-arg, misc]

        app_migrations_loader = MigrationsLoader(
            migrations_dir=build_dir / MIGRATIONS_DIR_NAME,
            module_type=ModuleType.USER,
            module_name=build_migrations_module_name(
                None,
                MIGRATIONS_DIR_NAME,
            ),
        )
        schemas = MigrationSchemas()

        executor = AsyncFileMigrationExecutorManager(
            core_migrations_path=CORE_MIGRATIONS_PATH,
            app_migrations_loader=app_migrations_loader,
            executor=DefaultAsyncMigrationExecutor(schemas),
            contrib=settings.CONTRIBS,
            contrib_migrations_directory_name=settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
        )

        if number and number.lower().strip() == 'zero':
            number = '-1'

        result: list[MigrationResult] = await executor.execute(
            migration_number=int(number) if number else None,
            module_type=module_type,
            fake=fake,
        )

        if not result:
            rprint(rich_info('Migrations are up to date'))
            return

        reverted = [item for item in result if item.direction == MigrationDirection.BACKWARD]
        applied = [item for item in result if item.direction == MigrationDirection.FORWARD]

        if reverted:
            rprint(rich_warning('Migrations reverted'))
        render_migrations_list([item.migration for item in reverted], color='yellow', is_migrated=False)

        if applied:
            rprint(rich_success('Migrations applied'))
            render_migrations_list([item.migration for item in applied], color='green', is_migrated=True)
    finally:
        await amsdal_manager.teardown()
        AsyncAmsdalManager.invalidate()


@sub_app.command(name='apply, apl, ap')
def apply_migrations(
    ctx: typer.Context,
    number: Annotated[
        str,  # noqa: RUF013
        typer.Option(
            '--number',
            '-n',
            help=(
                'Number of migration, e.g. 0002 or just 2. '
                'Use "zero" as a number to unapply all migrations including initial one.'
            ),
        ),
    ] = None,  # type: ignore[assignment]
    build_dir: Annotated[Path, typer.Option(..., '--build-dir', '-b')] = Path('.'),
    *,
    module_type: Annotated[ModuleType, typer.Option(..., '--module', '-m')] = ModuleType.USER.value,  # type: ignore
    fake: Annotated[bool, typer.Option('--fake', '-f')] = False,
    config: Annotated[Path, typer.Option(..., '--config', '-c')] = None,  # type: ignore # noqa: RUF013
) -> None:
    """
    Applies migrations to the application.

    This command applies migrations in the following order:

    1. Core migrations
    2. Contrib migrations
    3. App migrations

    Example of usage:

    1. Applies all pending migrations:
    ```bash
    amsdal migrations apply
    ```

    2. Applies all migrations up to a module type, e.g. CONTRIB:
    ```bash
    amsdal migrations apply --module contrib
    ```
    It will apply all core migrations + all contrib migrations

    3. Applies migrations up to a specific number:
    ```bash
    amsdal migrations apply --number 0002
    ```
    If you didn't specify the module type, it will apply migrations up to the specified number for the app module.

    4. Applies migrations in fake mode:
    ```bash
    amsdal migrations apply --fake
    ```
    It will apply all pending migrations in fake mode, so the actual changes will not be applied to the database.
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

    if AmsdalConfigManager().get_config().async_mode:
        asyncio.run(
            _async_sync_apply(
                number=number,
                build_dir=build_dir,
                module_type=module_type,
                fake=fake,
            )
        )
    else:
        _sync_apply(
            number=number,
            build_dir=build_dir,
            module_type=module_type,
            fake=fake,
        )
