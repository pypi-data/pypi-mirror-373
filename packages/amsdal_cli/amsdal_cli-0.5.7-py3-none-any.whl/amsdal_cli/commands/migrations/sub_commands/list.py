import asyncio
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Annotated

import typer
from rich import print as rprint

from amsdal_cli.commands.migrations.utils import render_migrations_list

if TYPE_CHECKING:
    from amsdal_models.migration.data_classes import MigrationFile


def _fetch_migrations(app_migrations_path: Path) -> list['MigrationFile']:
    from amsdal.manager import AmsdalManager
    from amsdal_models.migration.file_migration_store import FileMigrationStore

    amsdal_manager = AmsdalManager()
    if not amsdal_manager.is_setup:
        amsdal_manager.setup()
    amsdal_manager.authenticate()
    amsdal_manager.post_setup()  # type: ignore[call-arg]

    store = FileMigrationStore(app_migrations_path)
    store.init_migration_table()

    return store.fetch_migrations()


async def _async_fetch_migrations(app_migrations_path: Path) -> list['MigrationFile']:
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_models.migration.file_migration_store import AsyncFileMigrationStore

    amsdal_manager = AsyncAmsdalManager()
    if not amsdal_manager.is_setup:
        await amsdal_manager.setup()

    try:
        amsdal_manager.authenticate()
        await amsdal_manager.post_setup()  # type: ignore[call-arg,misc]

        store = AsyncFileMigrationStore(app_migrations_path)
        await store.init_migration_table()

        return await store.fetch_migrations()
    finally:
        await amsdal_manager.teardown()


def list_migrations(
    ctx: typer.Context,
    build_dir: Annotated[Path, typer.Option('--build-dir', '-b')] = Path('.'),
    *,
    config: Annotated[Path, typer.Option('--config', '-c')] = None,  # type: ignore # noqa: RUF013
) -> None:
    r"""
    Shows all migrations, which are applied and not applied including CORE and CONTRIB migrations.
    """
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal_models.migration.migrations_loader import MigrationsLoader
    from amsdal_models.migration.utils import build_migrations_module_name
    from amsdal_models.migration.utils import contrib_to_module_root_path
    from amsdal_utils.config.manager import AmsdalConfigManager
    from amsdal_utils.models.enums import ModuleType

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.text import rich_info

    if ctx.invoked_subcommand is not None:
        return

    cli_config: CliConfig = ctx.meta['config']

    app_builder = AppBuilder(
        cli_config=cli_config,
        config_path=config or cli_config.config_path,
    )
    app_builder.build(build_dir, is_silent=True)

    if AmsdalConfigManager().get_config().async_mode:
        _all_applied_migrations = asyncio.run(_async_fetch_migrations(build_dir / MIGRATIONS_DIR_NAME))
    else:
        _all_applied_migrations = _fetch_migrations(build_dir / MIGRATIONS_DIR_NAME)

    _core_applied_numbers = [_m.number for _m in _all_applied_migrations if _m.type == ModuleType.CORE]
    _app_applied_numbers = [_m.number for _m in _all_applied_migrations if _m.type == ModuleType.USER]
    _contrib_applied_numbers: dict[str, list[int]] = defaultdict(list)

    for _m in _all_applied_migrations:
        if _m.type == ModuleType.CONTRIB and _m.module:
            _contrib_applied_numbers[_m.module].append(_m.number)

    core_loader = MigrationsLoader(
        migrations_dir=CORE_MIGRATIONS_PATH,
        module_type=ModuleType.CORE,
        module_name=build_migrations_module_name(
            'amsdal',
            '__migrations__',
        ),
    )
    contrib_loaders: list[tuple[str, MigrationsLoader]] = []

    for contrib in settings.CONTRIBS:
        contrib_root_path = contrib_to_module_root_path(contrib)

        contrib_loaders.append(
            (
                contrib,
                MigrationsLoader(
                    migrations_dir=contrib_root_path / settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
                    module_type=ModuleType.CONTRIB,
                    module_name=build_migrations_module_name(
                        '.'.join(contrib.split('.')[:-2]),
                        settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
                    ),
                ),
            ),
        )

    app_migrations_loader = MigrationsLoader(
        migrations_dir=build_dir / MIGRATIONS_DIR_NAME,
        module_type=ModuleType.USER,
        module_name=build_migrations_module_name(
            None,
            MIGRATIONS_DIR_NAME,
        ),
    )

    all_migrations = list(core_loader)

    for _contrib, _loader in contrib_loaders:
        all_migrations.extend(list(_loader))

    def _is_migrated(migration: 'MigrationFile') -> bool:
        if migration.type == ModuleType.CORE:
            return migration.number in _core_applied_numbers

        if migration.type == ModuleType.CONTRIB:
            _applied_numbers = _contrib_applied_numbers[migration.module]  # type: ignore[index]
            return migration.number in _applied_numbers

        return migration.number in _app_applied_numbers

    def _color(migration: 'MigrationFile') -> str:
        _applied = 'green'
        _missing = 'grey'

        return _applied if _is_migrated(migration) else _missing

    render_migrations_list(
        all_migrations,
        color=_color,
        is_migrated=_is_migrated,
    )
    _app_migration_files = list(app_migrations_loader)

    if _app_migration_files:
        render_migrations_list(_app_migration_files, _color, is_migrated=_is_migrated)
    else:
        rprint(rich_info("You don't have any migrations in your app"))
