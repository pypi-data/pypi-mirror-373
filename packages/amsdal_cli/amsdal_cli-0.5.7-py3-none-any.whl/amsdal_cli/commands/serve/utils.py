import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from rich import print as rprint

if TYPE_CHECKING:
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_models.migration.base_migration_schemas import DefaultMigrationSchemas
    from amsdal_models.migration.data_classes import MigrationFile
    from amsdal_models.migration.migrations_loader import MigrationsLoader

    from amsdal_cli.utils.cli_config import CliConfig


def cleanup_app(output_path: Path, *, remove_warehouse: bool = True) -> None:
    """
    Cleanup the generated models and files after stopping.

    Args:
        output_path (Path): The path to the output directory.
        remove_warehouse (bool, optional): If True, remove the warehouse directory. Defaults to True.

    Returns:
        None
    """

    for path in (
        (output_path / 'transactions'),
        (output_path / 'migrations'),
        (output_path / 'models'),
        (output_path / 'schemas'),
        (output_path / 'fixtures'),
        (output_path / 'static'),
        (output_path / '.cache-thumbnails'),
    ):
        if not path.exists():
            continue
        shutil.rmtree(str(path.resolve()))

    warehouse_path = output_path / 'warehouse'

    if remove_warehouse and warehouse_path.exists():
        shutil.rmtree(str(warehouse_path.resolve()))


def build_app_and_check_migrations(
    cli_config: 'CliConfig',
    output_path: Path,
    app_source_path: Path,
    config_path: Path,
    *,
    apply_fixtures: bool = True,
    confirm_migrations: bool | None = False,
    skip_migrations_check: bool = False,
) -> 'AmsdalManager':
    """
    Builds the application and checks for migrations.

    Args:
        cli_config (CliConfig): CLI config
        output_path (Path): The path to the output directory.
        app_source_path (Path): The path to the application source directory.
        config_path (Path): The path to the configuration file.
        apply_fixtures (bool, optional): If True, apply fixtures to the database. Defaults to True.
        confirm_migrations (bool, optional): If True, confirm migrations before proceeding. Defaults to False.

    Returns:
        AmsdalManager: The Amsdal manager instance.
    """

    from amsdal.manager import AmsdalManager

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.utils.text import CustomConfirm
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    app_builder = AppBuilder(
        cli_config=cli_config,
        config_path=config_path,
    )
    app_builder.build(output_path, is_silent=True)

    amsdal_manager = AmsdalManager()
    amsdal_manager.pre_setup()
    if not amsdal_manager.is_setup:
        amsdal_manager.setup()

    if skip_migrations_check:
        return amsdal_manager

    has_unapplied = check_migrations_generated_and_applied(
        app_path=app_source_path.parent,
        build_dir=output_path,
        amsdal_manager=amsdal_manager,
        cli_config=cli_config,
    )

    if confirm_migrations and has_unapplied:
        run_server = CustomConfirm.ask(
            rich_info('Do you want to run server anyway?'),
            default=False,
            show_default=False,
            choices=['y', 'N'],
        )

        if not run_server:
            rprint(rich_error('Exiting...'))
            sys.exit(1)
    elif confirm_migrations is None:
        pass
    elif has_unapplied:
        rprint(rich_error('Exiting...'))
        sys.exit(1)

    if apply_fixtures:
        rprint(rich_info('Applying fixtures...'), end=' ')
        if not amsdal_manager.is_setup:
            amsdal_manager.setup()

        amsdal_manager.post_setup()  # type: ignore[call-arg]
        amsdal_manager.init_classes()

        if not amsdal_manager.is_authenticated:
            amsdal_manager.authenticate()

        amsdal_manager.apply_fixtures()  # type: ignore[call-arg]
        rprint(rich_success('OK!'))

    return amsdal_manager


def check_migrations_generated_and_applied(
    app_path: Path,
    build_dir: Path,
    amsdal_manager: 'AmsdalManager',
    cli_config: 'CliConfig',
) -> bool:
    """
    Check if migrations are generated and applied.

    Args:
        app_path (Path): The path to the application directory.
        build_dir (Path): The path to the build directory.
        amsdal_manager (AmsdalManager): The Amsdal manager instance.
        cli_config (CliConfig): CLI Config

    Returns:
        bool: True if there are unapplied migrations, False otherwise.
    """
    if not amsdal_manager.is_setup:
        amsdal_manager.setup()

    if not amsdal_manager.is_authenticated:
        amsdal_manager.authenticate()

    amsdal_manager.post_setup()  # type: ignore[call-arg]

    has_unapplied_migrations = _check_has_unapplied_migrations(build_dir=build_dir)

    if has_unapplied_migrations:
        return True

    return _check_migrations_generated_and_applied(app_path=app_path, cli_config=cli_config)


def _check_migrations_generated_and_applied(
    app_path: Path,
    cli_config: 'CliConfig',
) -> bool:
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal_models.migration.file_migration_generator import FileMigrationGenerator

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME
    from amsdal_cli.utils.cli_config import ModelsFormat
    from amsdal_cli.utils.schema_repository import build_schema_repository
    from amsdal_cli.utils.text import rich_warning

    app_source_path = app_path / cli_config.src_dir
    migrations_dir = app_source_path / MIGRATIONS_DIR_NAME

    cli_config.models_format = ModelsFormat.PY
    schema_repository = build_schema_repository(cli_config=cli_config)

    generator = FileMigrationGenerator(
        core_migrations_path=CORE_MIGRATIONS_PATH,
        app_migrations_path=migrations_dir,
        contrib_migrations_directory_name=settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
    )
    generator.init_state()

    operations = generator.app_file_migration_generator.generate_operations(schemas=schema_repository.user_schemas)

    if operations:
        rprint(
            rich_warning(
                'WARNING: you have changes in your models. Use "amsdal migrations new" to generate migrations.',
            )
        )

        return True
    return False


def _check_has_unapplied_migrations(
    build_dir: Path,
) -> bool:
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal_models.migration.base_migration_schemas import DefaultMigrationSchemas
    from amsdal_models.migration.file_migration_store import FileMigrationStore
    from amsdal_models.migration.migrations_loader import MigrationsLoader
    from amsdal_models.migration.utils import build_migrations_module_name
    from amsdal_models.migration.utils import contrib_to_module_root_path
    from amsdal_utils.models.enums import ModuleType

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME

    store = FileMigrationStore(build_dir / MIGRATIONS_DIR_NAME)
    all_applied_migrations = store.fetch_migrations()
    core_loader = MigrationsLoader(
        migrations_dir=CORE_MIGRATIONS_PATH,
        module_type=ModuleType.CORE,
        module_name=build_migrations_module_name(
            'amsdal',
            '__migrations__',
        ),
    )

    schemas = DefaultMigrationSchemas()

    if _check_has_unapplied_migrations_per_loader(core_loader, all_applied_migrations, schemas):
        return True

    for contrib in settings.CONTRIBS:
        contrib_root_path = contrib_to_module_root_path(contrib)

        if _check_has_unapplied_migrations_per_loader(
            MigrationsLoader(
                migrations_dir=contrib_root_path / settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
                module_type=ModuleType.CONTRIB,
                module_name=build_migrations_module_name(
                    '.'.join(contrib.split('.')[:-2]),
                    settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
                ),
            ),
            all_applied_migrations,
            schemas,
        ):
            return True

    return _check_has_unapplied_migrations_per_loader(
        MigrationsLoader(
            migrations_dir=build_dir / MIGRATIONS_DIR_NAME,
            module_type=ModuleType.USER,
            module_name=build_migrations_module_name(
                None,
                MIGRATIONS_DIR_NAME,
            ),
        ),
        all_applied_migrations,
        schemas,
    )


def _check_has_unapplied_migrations_per_loader(
    migration_loader: 'MigrationsLoader',
    all_applied_migrations: list['MigrationFile'],
    schemas: 'DefaultMigrationSchemas',
) -> bool:
    from amsdal_models.migration.executors.state_executor import StateMigrationExecutor
    from amsdal_models.migration.file_migration_executor import BaseMigrationExecutorManager
    from amsdal_models.migration.migrations import MigrateData

    from amsdal_cli.utils.text import rich_warning

    for _migration in migration_loader:
        if not _is_migration_applied(_migration, all_applied_migrations):
            rprint(
                rich_warning(
                    'WARNING: you have not applied all core migrations. Use "amsdal migrations apply" to apply them.',
                )
            )
            return True
        else:
            # Register classes from migrations

            migration_class = BaseMigrationExecutorManager.get_migration_class(_migration)
            migration_class_instance = migration_class()
            state_executor = StateMigrationExecutor(
                schemas,
                do_fetch_latest_version=True,
            )

            for _operation in migration_class_instance.operations:
                if isinstance(_operation, MigrateData):
                    continue

                _operation.forward(state_executor)
    return False


def _is_migration_applied(
    migration: 'MigrationFile',
    all_applied_migrations: list['MigrationFile'],
) -> bool:
    from amsdal_utils.models.enums import ModuleType

    for applied_migration in all_applied_migrations:
        is_applied = migration.type == applied_migration.type and migration.number == applied_migration.number

        if migration.type == ModuleType.CONTRIB.value:
            is_applied = is_applied and migration.module == applied_migration.module

        if is_applied:
            return True
    return False


async def async_build_app_and_check_migrations(
    cli_config: 'CliConfig',
    output_path: Path,
    app_source_path: Path,
    config_path: Path,
    *,
    apply_fixtures: bool = True,
    confirm_migrations: bool | None = False,
    skip_migrations_check: bool = False,
) -> 'AsyncAmsdalManager':
    """
    Builds the application and checks for migrations.

    Args:
        output_path (Path): The path to the output directory.
        app_source_path (Path): The path to the application source directory.
        config_path (Path): The path to the configuration file.
        apply_fixtures (bool, optional): If True, apply fixtures to the database. Defaults to True.
        confirm_migrations (bool, optional): If True, confirm migrations before proceeding. Defaults to False.

    Returns:
        AmsdalManager: The Amsdal manager instance.
    """
    from amsdal.manager import AsyncAmsdalManager

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.utils.text import CustomConfirm
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    app_builder = AppBuilder(
        cli_config=cli_config,
        config_path=config_path,
    )
    app_builder.build(output_path, is_silent=True)

    amsdal_manager = AsyncAmsdalManager()
    amsdal_manager.pre_setup()
    if not amsdal_manager.is_setup:
        await amsdal_manager.setup()

    if skip_migrations_check:
        return amsdal_manager

    try:
        has_unapplied = await async_check_migrations_generated_and_applied(
            app_path=app_source_path.parent,
            build_dir=output_path,
            amsdal_manager=amsdal_manager,
            cli_config=cli_config,
        )

        if confirm_migrations and has_unapplied:
            run_server = CustomConfirm.ask(
                rich_info('Do you want to run server anyway?'),
                default=False,
                show_default=False,
                choices=['y', 'N'],
            )

            if not run_server:
                rprint(rich_error('Exiting...'))
                sys.exit(1)
        elif confirm_migrations is None:
            pass
        elif has_unapplied:
            rprint(rich_error('Exiting...'))
            sys.exit(1)

        if apply_fixtures:
            rprint(rich_info('Applying fixtures...'), end=' ')
            if not amsdal_manager.is_setup:
                await amsdal_manager.setup()

            await amsdal_manager.post_setup()  # type: ignore[call-arg,misc]
            amsdal_manager.init_classes()

            if not amsdal_manager.is_authenticated:
                amsdal_manager.authenticate()

            await amsdal_manager.apply_fixtures()  # type: ignore[call-arg,misc]
            rprint(rich_success('OK!'))
    except Exception:
        if amsdal_manager.is_setup:
            await amsdal_manager.teardown()

        raise

    return amsdal_manager


async def async_check_migrations_generated_and_applied(
    app_path: Path,
    build_dir: Path,
    amsdal_manager: 'AsyncAmsdalManager',
    cli_config: 'CliConfig',
) -> bool:
    """
    Check if migrations are generated and applied.

    Args:
        app_path (Path): The path to the application directory.
        build_dir (Path): The path to the build directory.
        amsdal_manager (AsyncAmsdalManager): The Amsdal manager instance.
        cli_config (CliConfig): CLI Config

    Returns:
        bool: True if there are unapplied migrations, False otherwise.
    """
    if not amsdal_manager.is_setup:
        await amsdal_manager.setup()

    if not amsdal_manager.is_authenticated:
        amsdal_manager.authenticate()

    await amsdal_manager.post_setup()  # type: ignore[call-arg,misc]

    has_unapplied_migrations = await _async_check_has_unapplied_migrations(build_dir=build_dir)

    if has_unapplied_migrations:
        return True

    return await _async_check_migrations_generated_and_applied(app_path=app_path, cli_config=cli_config)


async def _async_check_has_unapplied_migrations(
    build_dir: Path,
) -> bool:
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal_models.migration.base_migration_schemas import DefaultMigrationSchemas
    from amsdal_models.migration.file_migration_store import AsyncFileMigrationStore
    from amsdal_models.migration.migrations_loader import MigrationsLoader
    from amsdal_models.migration.utils import build_migrations_module_name
    from amsdal_models.migration.utils import contrib_to_module_root_path
    from amsdal_utils.models.enums import ModuleType

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME

    store = AsyncFileMigrationStore(build_dir / MIGRATIONS_DIR_NAME)
    all_applied_migrations = await store.fetch_migrations()
    core_loader = MigrationsLoader(
        migrations_dir=CORE_MIGRATIONS_PATH,
        module_type=ModuleType.CORE,
        module_name=build_migrations_module_name(
            'amsdal',
            '__migrations__',
        ),
    )
    schemas = DefaultMigrationSchemas()

    if _check_has_unapplied_migrations_per_loader(core_loader, all_applied_migrations, schemas):
        return True

    for contrib in settings.CONTRIBS:
        contrib_root_path = contrib_to_module_root_path(contrib)

        if _check_has_unapplied_migrations_per_loader(
            MigrationsLoader(
                migrations_dir=contrib_root_path / settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
                module_type=ModuleType.CONTRIB,
                module_name=build_migrations_module_name(
                    '.'.join(contrib.split('.')[:-2]),
                    settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
                ),
            ),
            all_applied_migrations,
            schemas,
        ):
            return True

    return _check_has_unapplied_migrations_per_loader(
        MigrationsLoader(
            migrations_dir=build_dir / MIGRATIONS_DIR_NAME,
            module_type=ModuleType.USER,
            module_name=build_migrations_module_name(
                None,
                MIGRATIONS_DIR_NAME,
            ),
        ),
        all_applied_migrations,
        schemas,
    )


async def _async_check_migrations_generated_and_applied(
    app_path: Path,
    cli_config: 'CliConfig',
) -> bool:
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal_models.migration.file_migration_generator import AsyncFileMigrationGenerator

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME
    from amsdal_cli.utils.cli_config import ModelsFormat
    from amsdal_cli.utils.schema_repository import build_schema_repository
    from amsdal_cli.utils.text import rich_warning

    app_source_path = app_path / cli_config.src_dir
    migrations_dir = app_source_path / MIGRATIONS_DIR_NAME

    cli_config.models_format = ModelsFormat.PY
    schema_repository = build_schema_repository(cli_config=cli_config)

    generator = AsyncFileMigrationGenerator(
        core_migrations_path=CORE_MIGRATIONS_PATH,
        app_migrations_path=migrations_dir,
        contrib_migrations_directory_name=settings.CONTRIB_MIGRATIONS_DIRECTORY_NAME,
    )
    await generator.init_state()
    operations = generator.app_file_migration_generator.generate_operations(
        schemas=schema_repository.user_schemas,
    )

    if operations:
        rprint(
            rich_warning(
                'WARNING: you have changes in our models. Use "amsdal migrations new" to generate migrations.',
            )
        )

        return True
    return False
