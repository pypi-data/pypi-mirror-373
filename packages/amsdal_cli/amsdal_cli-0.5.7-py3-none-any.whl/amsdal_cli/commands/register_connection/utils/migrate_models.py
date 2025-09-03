import contextlib
import sys
import tempfile
from pathlib import Path

import yaml

from amsdal_cli.commands.register_connection.utils.build import build_models
from amsdal_cli.utils.cli_config import CliConfig


async def migrate_models_to_lakehouse(
    new_connection_name: str,
    cli_config: CliConfig,
    original_config_path: Path,
) -> None:
    from amsdal.configs.main import settings
    from amsdal_utils.config.manager import AmsdalConfigManager

    # swap amsdal config to lakehouse only
    config_manager = AmsdalConfigManager()
    config_manager.load_config(original_config_path)
    original_config = config_manager.get_config()

    with tempfile.TemporaryDirectory() as _temp_dir:
        temp_dir = Path(_temp_dir)
        config_path = temp_dir / 'config.yml'
        connection_name = original_config.resources_config.lakehouse
        lakehouse_connection = original_config.connections[connection_name]

        with config_path.open('w') as f:
            yaml.safe_dump(
                {
                    'application_name': original_config.application_name,
                    'connections': {
                        connection_name: lakehouse_connection.model_dump(),
                    },
                    'resources_config': {
                        'lakehouse': connection_name,
                        'repository': None,
                    },
                    'async_mode': original_config.async_mode,
                },
                f,
            )

        build_models(
            cli_config,
            config_path=config_path,
            build_dir=temp_dir,
        )

        sys.path.insert(0, str(settings.USER_MODELS_MODULE_PATH.absolute()))  # type: ignore[union-attr]

        if config_manager.get_config().async_mode:
            await _async_migrate_models(config_path)
        else:
            _migrate_models(config_path)

        config_manager.load_config(original_config_path)

        if config_manager.get_config().async_mode:
            await _async_migrate_data(new_connection_name)
        else:
            _migrate_data(new_connection_name)


def _migrate_models(config_path: Path) -> None:
    from amsdal.configs.main import settings
    from amsdal.manager import AmsdalManager
    from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager
    from amsdal_models.classes.class_loader import ModelClassLoader
    from amsdal_models.migration import migrations
    from amsdal_models.migration.executors.default_executor import DefaultMigrationExecutor
    from amsdal_models.migration.file_migration_generator import BaseFileMigrationGenerator
    from amsdal_models.migration.file_migration_writer import FileMigrationWriter
    from amsdal_models.migration.migrations import MigrationSchemas
    from amsdal_models.schemas.class_schema_loader import ClassSchemaLoader
    from amsdal_utils.config.manager import AmsdalConfigManager
    from amsdal_utils.models.enums import ModuleType

    # teardown the manager and connections
    manager = AmsdalManager()
    manager.teardown()

    # setup the new manager and connections
    AmsdalConfigManager().load_config(config_path)
    new_manager = AmsdalManager()
    if not new_manager.is_setup:
        new_manager.setup()
    new_manager.post_setup()  # type: ignore[call-arg]

    schemas = MigrationSchemas()
    executor = DefaultMigrationExecutor(schemas, use_foreign_keys=True)

    with contextlib.suppress(Exception):
        HistoricalSchemaVersionManager().object_classes  # noqa: B018

    core_class_loader = ModelClassLoader(settings.CORE_MODELS_MODULE)

    for _cls in core_class_loader.load(unload_module=True):
        if _cls.__module_type__ == ModuleType.CORE:
            schemas._classes[_cls.__name__] = _cls

    for contrib in settings.CONTRIBS:
        contrib_root = '.'.join(contrib.split('.')[:-2])

        _class_loader = ModelClassLoader(
            f'{contrib_root}.{settings.CONTRIB_MODELS_PACKAGE_NAME}',
        )

        for _cls in _class_loader.load(unload_module=True):
            if _cls.__module_type__ == ModuleType.CONTRIB:
                schemas._classes[_cls.__name__] = _cls

    user_schema_loader = ClassSchemaLoader(
        settings.USER_MODELS_MODULE,
        class_filter=lambda cls: cls.__module_type__ == ModuleType.USER,
    )
    _schemas, _cycle_schemas = user_schema_loader.load_sorted()
    _schemas_map = {_schema.title: _schema for _schema in _schemas}

    for object_schema in _schemas:
        for _operation_data in BaseFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            None,
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),  # type: ignore[union-attr]
            )

            _operation.forward(executor)

    for object_schema in _cycle_schemas:
        for _operation_data in BaseFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            _schemas_map[object_schema.title],
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),  # type: ignore[union-attr]
            )

            _operation.forward(executor)

    executor.flush_buffer()

    # teardown the manager and connections
    new_manager.teardown()


async def _async_migrate_models(config_path: Path) -> None:
    from amsdal.configs.main import settings
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager
    from amsdal_models.classes.class_loader import ModelClassLoader
    from amsdal_models.migration import migrations
    from amsdal_models.migration.executors.default_executor import DefaultAsyncMigrationExecutor
    from amsdal_models.migration.file_migration_generator import BaseFileMigrationGenerator
    from amsdal_models.migration.file_migration_writer import FileMigrationWriter
    from amsdal_models.migration.migrations import MigrationSchemas
    from amsdal_models.schemas.class_schema_loader import ClassSchemaLoader
    from amsdal_utils.config.manager import AmsdalConfigManager
    from amsdal_utils.models.enums import ModuleType

    # teardown the manager and connections
    manager = AsyncAmsdalManager()
    await manager.teardown()
    # setup the new manager and connections
    AmsdalConfigManager().load_config(config_path)
    new_manager = AsyncAmsdalManager()
    if not new_manager.is_setup:
        await new_manager.setup()
    await new_manager.post_setup()  # type: ignore[call-arg, misc]

    schemas = MigrationSchemas()
    executor = DefaultAsyncMigrationExecutor(schemas, use_foreign_keys=True)

    with contextlib.suppress(Exception):
        await AsyncHistoricalSchemaVersionManager().object_classes

    core_class_loader = ModelClassLoader(settings.CORE_MODELS_MODULE)

    for _cls in core_class_loader.load(unload_module=True):
        if _cls.__module_type__ == ModuleType.CORE:
            schemas._classes[_cls.__name__] = _cls

    for contrib in settings.CONTRIBS:
        contrib_root = '.'.join(contrib.split('.')[:-2])

        _class_loader = ModelClassLoader(
            f'{contrib_root}.{settings.CONTRIB_MODELS_PACKAGE_NAME}',
        )

        for _cls in _class_loader.load(unload_module=True):
            if _cls.__module_type__ == ModuleType.CONTRIB:
                schemas._classes[_cls.__name__] = _cls

    user_schema_loader = ClassSchemaLoader(
        settings.USER_MODELS_MODULE,
        class_filter=lambda cls: cls.__module_type__ == ModuleType.USER,
    )
    _schemas, _cycle_schemas = user_schema_loader.load_sorted()
    _schemas_map = {_schema.title: _schema for _schema in _schemas}

    for object_schema in _schemas:
        for _operation_data in BaseFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            None,
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),  # type: ignore[union-attr]
            )

            _operation.forward(executor)

    for object_schema in _cycle_schemas:
        for _operation_data in BaseFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            _schemas_map[object_schema.title],
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),  # type: ignore[union-attr]
            )

            _operation.forward(executor)

    await executor.flush_buffer()

    # teardown the manager and connections
    await new_manager.teardown()


def _migrate_data(new_connection_name: str) -> None:
    from amsdal.configs.main import settings
    from amsdal.manager import AmsdalManager
    from amsdal_data.aliases.using import DEFAULT_DB_ALIAS
    from amsdal_data.aliases.using import LAKEHOUSE_DB_ALIAS
    from amsdal_models.classes.class_loader import ModelClassLoader
    from amsdal_utils.models.enums import ModuleType

    origin_manager = AmsdalManager()
    if not origin_manager.is_setup:
        origin_manager.setup()
    origin_manager.post_setup()  # type: ignore[call-arg]

    model_class_loader = ModelClassLoader(settings.USER_MODELS_MODULE)
    tables_for_connection = _resolve_tables_for_connection(new_connection_name)

    for model_class in model_class_loader.load(unload_module=True):
        if model_class.__table_name__ not in tables_for_connection:
            continue

        if model_class.__module_type__ == ModuleType.USER:
            page = 0
            page_size = 250

            while True:
                qs = model_class.objects.using(DEFAULT_DB_ALIAS)[slice(page * page_size, page * page_size + page_size)]
                data = qs.execute()
                page += 1

                if not data:
                    break

                for item in data:
                    lakehouse_qs = (
                        model_class.objects.using(LAKEHOUSE_DB_ALIAS)
                        .latest()
                        .get_or_none(
                            _address__object_id=item.object_id,
                        )
                    )
                    lakehouse_item = lakehouse_qs.execute()
                    force_insert = False

                    if not lakehouse_item:
                        force_insert = True
                        lakehouse_item = model_class(**item.model_dump_refs())

                    lakehouse_item.save(
                        force_insert=force_insert,
                        using=LAKEHOUSE_DB_ALIAS,
                    )


async def _async_migrate_data(new_connection_name: str) -> None:
    from amsdal.configs.main import settings
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_data.aliases.using import DEFAULT_DB_ALIAS
    from amsdal_data.aliases.using import LAKEHOUSE_DB_ALIAS
    from amsdal_models.classes.class_loader import ModelClassLoader
    from amsdal_utils.models.enums import ModuleType

    origin_manager = AsyncAmsdalManager()
    if not origin_manager.is_setup:
        await origin_manager.setup()
    await origin_manager.post_setup()  # type: ignore[call-arg, misc]

    model_class_loader = ModelClassLoader(settings.USER_MODELS_MODULE)
    tables_for_connection = _resolve_tables_for_connection(new_connection_name)

    for model_class in model_class_loader.load(unload_module=True):
        if model_class.__table_name__ not in tables_for_connection:
            continue

        if model_class.__module_type__ == ModuleType.USER:
            page = 0
            page_size = 250

            while True:
                qs = model_class.objects.using(DEFAULT_DB_ALIAS)[slice(page * page_size, page * page_size + page_size)]
                data = await qs.aexecute()
                page += 1

                if not data:
                    break

                for item in data:
                    lakehouse_qs = (
                        model_class.objects.using(LAKEHOUSE_DB_ALIAS)
                        .latest()
                        .get_or_none(
                            _address__object_id=item.object_id,
                        )
                    )
                    lakehouse_item = await lakehouse_qs.aexecute()
                    force_insert = False

                    if not lakehouse_item:
                        force_insert = True
                        lakehouse_item = model_class(**item.model_dump_refs())

                    await lakehouse_item.asave(  # type: ignore[misc]
                        force_insert=force_insert,
                        using=LAKEHOUSE_DB_ALIAS,
                    )

    await origin_manager.teardown()


def _resolve_tables_for_connection(connection_name: str) -> list[str]:
    from amsdal_utils.config.manager import AmsdalConfigManager

    config = AmsdalConfigManager().get_config()
    tables = config.resources_config.repository.models  # type: ignore[union-attr]

    return [table for table in tables if tables[table] == connection_name]
