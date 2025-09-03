import asyncio
import sys
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import amsdal_glue as glue
import typer
from amsdal_data.connections.historical.data_query_transform import METADATA_TABLE_ALIAS
from amsdal_models.querysets.executor import LAKEHOUSE_DB_ALIAS
from amsdal_utils.models.data_models.enums import CoreTypes
from rich import print as rprint

from amsdal_cli.app import app
from amsdal_cli.commands.restore.enums import RestoreType

if TYPE_CHECKING:
    from amsdal_utils.config.data_models.amsdal_config import AmsdalConfig
    from amsdal_utils.schemas.schema import ObjectSchema

    from amsdal_cli.utils.cli_config import CliConfig


@app.command(name='restore, rst')
def restore_command(
    ctx: typer.Context,
    restore_type: RestoreType = RestoreType.MODELS,
    *,
    config: Path = typer.Option(None, help='Path to custom config.yml file'),  # noqa: B008
) -> None:
    """
    Restores either models or state database from the lakehouse.

    Example of usage:

    1. Restore models:
    ```bash
    amsdal restore models --config config.yml
    ```

    2. Restore state database:
    ```bash
    amsdal restore state_db --config config.yml
    ```
    """
    from amsdal_cli.utils.cli_config import CliConfig

    cli_config: CliConfig = ctx.meta['config']

    if restore_type == RestoreType.MODELS:
        _restore_models(cli_config, config)
    else:
        _restore_state_db(cli_config, config)


def _restore_models(cli_config: 'CliConfig', config: Path | None) -> None:
    from amsdal_utils.config.manager import AmsdalConfigManager

    from amsdal_cli.commands.build.services.builder import AppBuilder

    app_source_path = cli_config.app_directory / cli_config.src_dir
    app_source_path.mkdir(exist_ok=True)

    app_builder = AppBuilder(
        cli_config=cli_config,
        config_path=config or cli_config.config_path,
    )
    app_builder.build(Path('.'))

    if AmsdalConfigManager().get_config().async_mode:
        asyncio.run(_async_restore_models(app_source_path, cli_config))
    else:
        _sync_restore_models(app_source_path, cli_config)


def _sync_restore_models(app_source_path: Path, cli_config: 'CliConfig') -> None:
    from amsdal.configs.main import settings
    from amsdal.manager import AmsdalManager
    from amsdal_models.builder.services.class_builder import ClassBuilder
    from amsdal_models.classes.class_manager import ClassManager
    from amsdal_utils.models.enums import ModuleType
    from amsdal_utils.models.enums import Versions
    from amsdal_utils.schemas.schema import ObjectSchema
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.utils.cli_config import ModelsFormat
    from amsdal_cli.utils.schema_repository import build_schema_repository
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    amsdal_manager = AmsdalManager()
    if not amsdal_manager.is_setup:
        amsdal_manager.setup()
    amsdal_manager.authenticate()
    amsdal_manager.register_internal_classes()
    class_manager = ClassManager()

    rprint(rich_info('Reading classes...'))
    class_object_model = class_manager.import_class('ClassObject', ModuleType.CORE)
    class_object_meta_model = class_manager.import_class('ClassObjectMeta', ModuleType.CORE)
    class_objects = (
        class_object_model.objects.using(LAKEHOUSE_DB_ALIAS)
        .filter(
            _address__class_version=Versions.LATEST,
            _address__object_version=Versions.LATEST,
            _metadata__is_deleted=False,
        )
        .execute()
    )
    class_object_metas = (
        class_object_meta_model.objects.using(LAKEHOUSE_DB_ALIAS)
        .filter(
            class_schema_type=ModuleType.USER,
            _address__class_version=Versions.LATEST,
            _address__object_version=Versions.LATEST,
            _metadata__is_deleted=False,
        )
        .execute()
    )

    rprint(f'[yellow]Found {len(class_objects)} classes...[/yellow]')

    for class_object_meta in class_object_metas:
        class_object = next(
            (class_object for class_object in class_objects if class_object.object_id == class_object_meta.title),
            None,
        )
        if not class_object:
            msg = f'Class object not found for class object meta: "{class_object_meta.title}".'
            raise ValueError(msg)

        json_schema = class_object.model_dump()
        meta = class_object_meta.model_dump()
        meta_props = meta.pop('properties', {})

        for prop_name, prop in json_schema.get('properties', {}).items():
            prop.update(meta_props.get(prop_name, {}))

        json_schema.update(meta)
        object_schema = ObjectSchema(**json_schema)

        class_name = class_object.object_id
        rprint(rich_info(f'Restoring {class_name}...'), end=' ')

        if cli_config.models_format == ModelsFormat.JSON:
            model_path = app_source_path / 'models' / to_snake_case(class_name) / 'model.json'
            model_path.parent.mkdir(exist_ok=True, parents=True)
            model_path.write_text(object_schema.model_dump_json(indent=cli_config.indent))
        else:
            output_path = app_source_path / 'models'
            output_path.mkdir(exist_ok=True, parents=True)
            (output_path / '__init__.py').touch(exist_ok=True)

            sys.path.insert(0, str(app_source_path.absolute()))

            schema_repository = build_schema_repository(cli_config=cli_config, skip_user_models=True)
            class_builder = ClassBuilder()

            class_builder.build(
                models_package_path=output_path,
                models_module_path=settings.USER_MODELS_MODULE,
                object_schema=object_schema,
                module_type=ModuleType.USER,
                dependencies=schema_repository.model_module_info,  # type: ignore[arg-type]
                indent_width=' ' * cli_config.indent,
            )

        rprint(rich_success('Restored!'))

    rprint()
    rprint(rich_success('Done! All classes are restored.'))


async def _async_restore_models(app_source_path: Path, cli_config: 'CliConfig') -> None:
    from amsdal.configs.main import settings
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_models.builder.services.class_builder import ClassBuilder
    from amsdal_models.classes.class_manager import ClassManager
    from amsdal_utils.models.enums import ModuleType
    from amsdal_utils.models.enums import Versions
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.utils.cli_config import ModelsFormat
    from amsdal_cli.utils.schema_repository import build_schema_repository
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    amsdal_manager = AsyncAmsdalManager()
    if not amsdal_manager.is_setup:
        await amsdal_manager.setup()
    amsdal_manager.authenticate()
    amsdal_manager.register_internal_classes()
    class_manager = ClassManager()

    rprint(rich_info('Reading classes...'))
    class_object_model = class_manager.import_class('ClassObject', ModuleType.CORE)
    class_object_meta_model = class_manager.import_class('ClassObjectMeta', ModuleType.CORE)
    class_objects = await class_object_model.objects.filter(
        _address__class_version=Versions.LATEST,
        _address__object_version=Versions.LATEST,
        _metadata__is_deleted=False,
    ).aexecute()
    class_object_metas = await class_object_meta_model.objects.filter(
        class_schema_type=ModuleType.USER,
        _address__class_version=Versions.LATEST,
        _address__object_version=Versions.LATEST,
        _metadata__is_deleted=False,
    ).aexecute()

    rprint(f'[yellow]Found {len(class_objects)} classes...[/yellow]')

    for class_object_meta in class_object_metas:
        class_object = next(
            (class_object for class_object in class_objects if class_object.object_id == class_object_meta.title),
            None,
        )
        if not class_object:
            msg = f'Class object not found for class object meta: "{class_object_meta.title}".'
            raise ValueError(msg)

        json_schema = class_object.model_dump()
        meta = class_object_meta.model_dump()
        meta_props = meta.pop('properties', {})

        for prop_name, prop in json_schema.get('properties', {}).items():
            prop.update(meta_props.get(prop_name, {}))

        json_schema.update(meta)
        object_schema = ObjectSchema(**json_schema)

        class_name = class_object.object_id
        rprint(rich_info(f'Restoring {class_name}...'), end=' ')

        if cli_config.models_format == ModelsFormat.JSON:
            model_path = app_source_path / 'models' / to_snake_case(class_name) / 'model.json'
            model_path.parent.mkdir(exist_ok=True, parents=True)
            model_path.write_text(object_schema.model_dump_json(indent=cli_config.indent))
        else:
            output_path = app_source_path / 'models'
            output_path.mkdir(exist_ok=True, parents=True)
            (output_path / '__init__.py').touch(exist_ok=True)

            sys.path.insert(0, str(app_source_path.absolute()))

            schema_repository = build_schema_repository(cli_config=cli_config)
            class_builder = ClassBuilder()

            class_builder.build(
                models_package_path=output_path,
                models_module_path=settings.USER_MODELS_MODULE,
                object_schema=object_schema,
                module_type=ModuleType.USER,
                dependencies=schema_repository.model_module_info,  # type: ignore[arg-type]
                indent_width=' ' * cli_config.indent,
            )

        rprint(rich_success('Restored!'))

    rprint()
    rprint(rich_success('Done! All classes are restored.'))


def _restore_state_db(cli_config: 'CliConfig', config_path: Path | None) -> None:
    from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
    from amsdal_data.connections.historical.data_query_transform import META_FOREIGN_KEYS
    from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY_FIELDS
    from amsdal_data.utils import object_schema_to_glue_schema
    from amsdal_utils.config.manager import AmsdalConfigManager

    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    config_manager = AmsdalConfigManager()
    config_manager.load_config(config_path or cli_config.config_path)
    lakehouse_connection = _get_lakehouse_connection(config_manager.get_config())
    state_connection = _get_state_connection(config_manager.get_config())

    class_object_ref, class_object_meta_ref = _get_class_object_reference(lakehouse_connection)
    model_pks, model_fks, model_m2ms = _fetch_model_pks_and_fks(lakehouse_connection, class_object_ref)

    expected_m2m_tables: set[str] = set()
    for model_name, m2m_list in model_m2ms.items():
        for _, m2m_value in m2m_list.items():
            expected_m2m_tables.add(f'{model_name}{m2m_value[1]}')

    user_schemas = _get_user_schemas(
        lakehouse_connection,
        class_object_ref,
        class_object_meta_ref,
        model_fks=model_fks,
        model_pks=model_pks,  # type: ignore[arg-type]
    )
    user_scheams_with_tries = [(table_ref, schema, 0) for table_ref, schema in user_schemas]
    refs_by_name = {table_ref.name: table_ref for table_ref, _ in user_schemas}

    m2m_schemas = [schema for schema in user_schemas if schema[0].name in expected_m2m_tables]

    while user_scheams_with_tries:
        table_ref, schema, current_iteration = user_scheams_with_tries.pop(0)
        rprint(rich_info(f'Restoring {table_ref.name}'))
        glue_schema = object_schema_to_glue_schema(schema, use_foreign_keys=True)

        try:
            state_connection.run_schema_command(
                glue.SchemaCommand(
                    mutations=[
                        glue.RegisterSchema(
                            schema=glue_schema,
                        ),
                    ],
                ),
            )
        except Exception:
            if current_iteration < 3:  # noqa: PLR2004
                user_scheams_with_tries.append((table_ref, schema, current_iteration + 1))
                continue
            else:
                raise

        for item in _get_all_latest_data(lakehouse_connection, table_ref):
            item.pop(SECONDARY_PARTITION_KEY, None)
            item.pop('_metadata', None)

            from amsdal_data.connections.historical.data_query_transform import META_CLASS_NAME

            data, _ = _build_data(
                item,
                model_name=table_ref.metadata[META_CLASS_NAME],  # type: ignore[index]
                model_pks=model_pks,
                model_fks=model_fks,
                model_m2ms=model_m2ms,
                refs_by_name=refs_by_name,
            )

            state_connection.run_mutations(
                mutations=[
                    glue.InsertData(
                        schema=glue.SchemaReference(
                            name=table_ref.name,
                            version=glue.Version.LATEST,
                            metadata=table_ref.metadata,
                        ),
                        data=[data],
                    ),
                ],
            )
            rprint('.', end='')

    rprint('Inserting m2m data...')
    m2m_all_data = []
    for schema_ref, schema in m2m_schemas:
        _datas = []
        _objects = lakehouse_connection.query(glue.QueryStatement(table=schema_ref))
        field1, field2 = schema.required
        prop1 = schema.properties[field1]  # type: ignore[index]
        prop2 = schema.properties[field2]  # type: ignore[index]

        rprint(rich_info(f'Found {len(_objects)} m2m objects for {schema_ref.name}...'))
        for _item in _objects:
            obj_id_1 = _item.data[field1]['ref']['object_id']
            obj_id_2 = _item.data[field2]['ref']['object_id']
            _datas.append(
                glue.Data(
                    data={
                        f'{field1}_partition_key': obj_id_1,
                        f'{field2}_partition_key': obj_id_2,
                    },
                    metadata={
                        META_PRIMARY_KEY_FIELDS: {
                            f'{field1}_partition_key': str,
                            f'{field2}_partition_key': str,
                        },
                        META_FOREIGN_KEYS: {
                            f'{field1}_partition_key': {
                                'ref': {
                                    'resource': 'statedb',
                                    'class_name': prop1.type,
                                    'object_id': obj_id_1,
                                    'class_version': 'LATEST',
                                    'object_version': 'LATEST',
                                },
                            },
                            f'{field2}_partition_key': {
                                'ref': {
                                    'resource': 'statedb',
                                    'class_name': prop2.type,
                                    'object_id': obj_id_2,
                                    'class_version': 'LATEST',
                                    'object_version': 'LATEST',
                                },
                            },
                        },
                    },
                )
            )

        if _datas:
            m2m_all_data.append(
                glue.InsertData(
                    schema=glue.SchemaReference(
                        name=schema_ref.name,
                        version=glue.Version.LATEST,
                        metadata=schema_ref.metadata,
                    ),
                    data=_datas,
                )
            )
    for _m2m_data in m2m_all_data:
        for data in _m2m_data.data:
            try:
                state_connection.run_mutations(
                    mutations=[
                        glue.InsertData(
                            schema=_m2m_data.schema,
                            data=[data],
                        ),
                    ]
                )
            except Exception:
                rprint('Error inserting m2m data')

    rprint(rich_success('Done! All classes are restored.'))


def _build_data(
    item: dict[str, Any],
    model_name: str,
    model_pks: dict[str, dict[str, type | glue.Schema | glue.SchemaReference]],
    model_fks: dict[str, Any],
    model_m2ms: dict[str, Any],
    refs_by_name: dict[str, glue.SchemaReference],
) -> tuple[glue.Data, list[glue.InsertData]]:
    from amsdal_data.connections.historical.data_query_transform import META_FOREIGN_KEYS
    from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY_FIELDS

    pks = model_pks[model_name]
    fks = model_fks.get(model_name, {})
    m2ms = model_m2ms.get(model_name, {})
    data = {}
    foreign_keys_meta = {}
    m2m_inserts = []

    for _name, _value in item.items():
        fk = fks.get(_name)
        m2m = m2ms.get(_name)

        if fk:
            _fields = list(fk[0].keys())
            foreign_keys_meta[_name] = (_value, _fields)

            if _value:
                _object_id = _value['ref']['object_id']

                if not isinstance(_object_id, list):
                    _object_id = [_object_id]
            else:
                _object_id = [None] * len(_fields)

            for _field, object_id in zip(_fields, _object_id, strict=False):
                data[_field] = object_id
        elif m2m:
            target_model_name = m2m[1]

            m2m_table_name = f'{model_name}{target_model_name}'
            m2m_table_ref = refs_by_name.get(m2m_table_name)
            if not m2m_table_ref:
                continue

            _datas = []

            for _val in _value:
                _datas.append(
                    glue.Data(
                        data={
                            f'{model_name.lower()}_partition_key': item['partition_key'],
                            f'{target_model_name.lower()}_partition_key': _val['ref']['object_id'],
                        },
                        metadata={
                            META_PRIMARY_KEY_FIELDS: {
                                f'{model_name.lower()}_partition_key': str,
                                f'{target_model_name.lower()}_partition_key': str,
                            },
                            META_FOREIGN_KEYS: {
                                f'{model_name.lower()}_partition_key': {
                                    'ref': {
                                        'resource': 'statedb',
                                        'class_name': model_name,
                                        'object_id': item['partition_key'],
                                        'class_version': 'LATEST',
                                        'object_version': 'LATEST',
                                    },
                                },
                                f'{target_model_name.lower()}_partition_key': {
                                    'ref': {
                                        'resource': 'statedb',
                                        'class_name': target_model_name,
                                        'object_id': _val['ref']['object_id'],
                                        'class_version': 'LATEST',
                                        'object_version': 'LATEST',
                                    },
                                },
                            },
                        },
                    )
                )

            m2m_inserts.append(
                glue.InsertData(
                    schema=glue.SchemaReference(
                        name=m2m_table_ref.name,
                        version=glue.Version.LATEST,
                        metadata=m2m_table_ref.metadata,
                    ),
                    data=_datas,
                ),
            )
        else:
            data[_name] = _value

    _data = glue.Data(
        data=data,
        metadata={
            META_PRIMARY_KEY_FIELDS: pks,
            META_FOREIGN_KEYS: foreign_keys_meta,
        },
    )
    return _data, m2m_inserts


def _get_lakehouse_connection(config: 'AmsdalConfig') -> glue.SqliteConnection | glue.PostgresConnection:
    connection_name = config.resources_config.lakehouse

    return _get_connection(connection_name, config)


def _get_state_connection(config: 'AmsdalConfig') -> glue.SqliteConnection | glue.PostgresConnection:
    connection_name = config.resources_config.repository.default  # type: ignore[union-attr]

    return _get_connection(connection_name, config)


def _get_connection(connection_name: str, config: 'AmsdalConfig') -> glue.SqliteConnection | glue.PostgresConnection:
    from amsdal_data.connections.db_alias_map import CONNECTION_BACKEND_ALIASES
    from amsdal_utils.utils.classes import import_class

    creds = config.connections[connection_name].credentials
    backend_alias = config.connections[connection_name].backend
    backend = import_class(CONNECTION_BACKEND_ALIASES.get(backend_alias, backend_alias))
    connection = backend()
    connection.connect(**creds)

    return connection


def _fetch_model_pks_and_fks(
    connection: glue.SqliteConnection | glue.PostgresConnection,
    class_object_ref: glue.SchemaReference,
) -> tuple[
    dict[str, dict[str, type | glue.Schema | glue.SchemaReference]],
    dict[str, dict[str, tuple[dict[str, Any], str, list[str]]]],
    dict[str, dict[str, tuple[dict[str, Any], str, list[str]]]],
]:
    from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY

    schemas = list(_get_all_latest_data(connection, class_object_ref))

    pk_data: dict[str, dict[str, type | glue.Schema | glue.SchemaReference]] = {
        schema[PRIMARY_PARTITION_KEY]: _build_pks(schema, all_schemas=schemas) for schema in schemas
    }
    fk_data: dict[str, dict[str, tuple[dict[str, Any], str, list[str]]]] = {}
    m2m_data: dict[str, dict[str, tuple[dict[str, Any], str, list[str]]]] = {}

    for schema in schemas:
        fk_data[schema[PRIMARY_PARTITION_KEY]], m2m_data[schema[PRIMARY_PARTITION_KEY]] = _build_fks(
            schema, all_schemas=schemas
        )

    return pk_data, fk_data, m2m_data


def _build_fks(
    schema: dict[str, Any],
    all_schemas: list[dict[str, Any]],
) -> tuple[
    dict[str, tuple[dict[str, Any], str, list[str]]],
    dict[str, tuple[dict[str, Any], str, list[str]]],
]:
    fks: dict[str, tuple[dict[str, str], str, list[str]]] = {}
    m2ms: dict[str, tuple[dict[str, str], str, list[str]]] = {}

    for prop_name, prop in schema['properties'].items():
        if prop['type'] == CoreTypes.ARRAY.value:
            _type = prop['items']['type']
            is_m2m = True
        else:
            _type = prop['type']
            is_m2m = False

        schema_type = get_schema_ref(_type, all_schemas)
        if schema_type:
            if is_m2m:
                m2ms[prop_name] = (
                    _build_fields(prop_name, prop.get('db_field'), schema_type, all_schemas),
                    schema_type['table_name'],
                    schema_type['primary_key'],
                )
            else:
                fks[prop_name] = (
                    _build_fields(prop_name, prop.get('db_field'), schema_type, all_schemas),
                    schema_type['table_name'],
                    schema_type['primary_key'],
                )
    return fks, m2ms


def _build_pks(
    schema: dict[str, Any],
    all_schemas: list[dict[str, Any]],
) -> dict[str, type | glue.Schema | glue.SchemaReference]:
    from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY

    pks: dict[str, type | glue.Schema | glue.SchemaReference] = {}
    primary_key = schema.get('primary_key') or [PRIMARY_PARTITION_KEY]

    if primary_key == [PRIMARY_PARTITION_KEY]:
        pks[PRIMARY_PARTITION_KEY] = str
    else:
        for field in primary_key:
            prop = schema['properties'][field]
            db_field = prop.get('db_field')

            if prop['type'] == CoreTypes.ARRAY.value:
                _type = prop['items']['type']
            else:
                _type = prop['type']

            schema_ref = get_schema_ref(_type, all_schemas)

            if schema_ref:
                _nested_pks = _build_pks(schema_ref, all_schemas)
                _db_fields = db_field or [f'{field}_{_nested_pk}' for _nested_pk in _nested_pks]

                for _nested_pk, _db_field in zip(_nested_pks, _db_fields, strict=False):
                    pks[_db_field] = _nested_pks[_nested_pk]

            else:
                from amsdal_data.utils import object_schema_type_to_glue_type

                pks[field] = object_schema_type_to_glue_type(prop['type'])  # type: ignore[assignment]

    return pks


def get_schema_ref(_type: str, schemas: list[dict[str, Any]]) -> dict[str, Any] | None:
    from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY

    for schema in schemas:
        if schema[PRIMARY_PARTITION_KEY] == _type:
            return schema
    return None


def _build_fields(
    prop_name: str,
    db_field: list[str] | None,
    schema_type: dict[str, Any],
    all_schemas: list[dict[str, Any]],
) -> dict[str, str]:
    from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY

    db_fields = {}
    pks = schema_type['primary_key']

    if pks == [PRIMARY_PARTITION_KEY]:
        _db_field = db_field[0] if db_field else f'{prop_name}_{PRIMARY_PARTITION_KEY}'
        db_fields[_db_field] = CoreTypes.STRING.value

        return db_fields

    if not db_field:
        db_field = [f'{prop_name}_{pk}' for pk in pks]

    _db_field_index = 0

    for pk in pks:
        prop = schema_type['properties'][pk]
        nested_db_field = prop.get('db_field')

        if prop['type'] == CoreTypes.ARRAY.value:
            _type = prop['items']['type']
        else:
            _type = prop['type']

        nested_schema_type = get_schema_ref(_type, all_schemas)

        if nested_schema_type:
            _nested_fields = _build_fields(pk, nested_db_field, nested_schema_type, all_schemas)

            for _nested_field in _nested_fields:
                db_fields[db_field[_db_field_index]] = _nested_fields[_nested_field]
                _db_field_index += 1
        else:
            db_fields[db_field[_db_field_index]] = prop['type']
            _db_field_index += 1

    return db_fields


def _get_class_object_reference(
    connection: glue.SqliteConnection | glue.PostgresConnection,
) -> tuple[glue.SchemaReference, glue.SchemaReference]:
    from amsdal_data.connections.constants import CLASS_OBJECT_META
    from amsdal_data.connections.constants import OBJECT_TABLE
    from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
    from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
    from amsdal_data.connections.historical.data_query_transform import build_simple_query_statement_with_metadata
    from amsdal_utils.models.data_models.enums import BaseClasses

    table = glue.SchemaReference(
        name=OBJECT_TABLE,
        version='',
    )
    conditions = glue.Conditions(
        glue.Condition(
            left=glue.FieldReferenceExpression(
                field_reference=glue.FieldReference(
                    field=glue.Field(name=PRIMARY_PARTITION_KEY),
                    table_name=table.name,
                ),
            ),
            lookup=glue.FieldLookup.EQ,
            right=glue.Value(BaseClasses.CLASS_OBJECT.value),
        ),
    )
    _add_latest_condition(conditions)

    query = build_simple_query_statement_with_metadata(
        table=table,
        where=conditions,
        limit=glue.LimitQuery(limit=1),
    )

    result = connection.query(query)

    if not result:
        msg = 'No class object found in the database.'
        raise ValueError(msg)

    conditions_meta = glue.Conditions(
        glue.Condition(
            left=glue.FieldReferenceExpression(
                field_reference=glue.FieldReference(
                    field=glue.Field(name=PRIMARY_PARTITION_KEY),
                    table_name=table.name,
                ),
            ),
            lookup=glue.FieldLookup.EQ,
            right=glue.Value(CLASS_OBJECT_META),
        ),
    )
    _add_latest_condition(conditions_meta)

    query_meta = build_simple_query_statement_with_metadata(
        table=table,
        where=conditions_meta,
        limit=glue.LimitQuery(limit=1),
    )

    result_meta = connection.query(query_meta)

    if not result_meta:
        msg = 'No class object meta found in the database.'
        raise ValueError(msg)

    class_object_data = result[0].data
    class_object_meta_data = result_meta[0].data

    _class_object_ref = glue.SchemaReference(
        name=BaseClasses.CLASS_OBJECT.value,
        version=class_object_data[SECONDARY_PARTITION_KEY],
    )
    _class_object_meta_ref = glue.SchemaReference(
        name=CLASS_OBJECT_META,
        version=class_object_meta_data[SECONDARY_PARTITION_KEY],
    )

    return _class_object_ref, _class_object_meta_ref


def _add_latest_condition(conditions: glue.Conditions) -> None:
    from amsdal_data.connections.historical.data_query_transform import METADATA_TABLE_ALIAS
    from amsdal_data.connections.historical.data_query_transform import NEXT_VERSION_FIELD

    conditions.children.append(
        glue.Conditions(
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=NEXT_VERSION_FIELD),
                        table_name=METADATA_TABLE_ALIAS,
                    ),
                ),
                lookup=glue.FieldLookup.ISNULL,
                right=glue.Value(value=True),
            ),
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=NEXT_VERSION_FIELD),
                        table_name=METADATA_TABLE_ALIAS,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(value=''),
            ),
            connector=glue.FilterConnector.OR,
        )
    )


def _get_user_schemas(
    connection: glue.SqliteConnection | glue.PostgresConnection,
    class_object_ref: glue.SchemaReference,
    class_object_meta_ref: glue.SchemaReference,
    model_fks: dict[str, Any],
    model_pks: dict[str, type],
) -> list[tuple[glue.SchemaReference, 'ObjectSchema']]:
    from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
    from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
    from amsdal_data.utils import FOREIGN_KEYS_PROPERTY
    from amsdal_utils.schemas.schema import ObjectSchema

    schemas = []

    for schema_data in _get_all_latest_data(connection, class_object_ref):
        class_version = schema_data.pop(SECONDARY_PARTITION_KEY, None)
        meta_conditions = glue.Conditions(
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=PRIMARY_PARTITION_KEY),
                        table_name=class_object_meta_ref.name,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(schema_data[PRIMARY_PARTITION_KEY]),
            ),
        )
        _add_latest_condition(meta_conditions)
        from amsdal_data.connections.historical.data_query_transform import build_simple_query_statement_with_metadata

        query_meta = build_simple_query_statement_with_metadata(
            table=class_object_meta_ref,
            where=meta_conditions,
            limit=glue.LimitQuery(limit=1),
        )

        result_meta = connection.query(query_meta)

        if not result_meta:
            msg = f'No class object meta found for {schema_data[PRIMARY_PARTITION_KEY]}'
            raise ValueError(msg)

        meta_data = result_meta[0].data
        meta_props = meta_data.pop('properties')
        schema_data.update(meta_data)

        if meta_props:
            for prop in meta_props:
                if prop not in schema_data['properties']:
                    schema_data['properties'][prop] = meta_props[prop]
                else:
                    schema_data['properties'][prop].update(meta_props[prop])

        for name, prop in schema_data['properties'].items():
            prop['field_name'] = name

        schema_data.pop('_metadata', None)
        schema_data.pop(PRIMARY_PARTITION_KEY, None)
        schema_data[FOREIGN_KEYS_PROPERTY] = model_fks.get(schema_data['title']) or {}

        from amsdal_data.connections.historical.data_query_transform import META_CLASS_NAME
        from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY
        from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY_FIELDS

        schemas.append(
            (
                glue.SchemaReference(
                    name=schema_data['title'],
                    version=class_version or '',
                    metadata={
                        META_PRIMARY_KEY: schema_data.get('primary_key', []),
                        META_PRIMARY_KEY_FIELDS: model_pks.get(schema_data['title'], {}),
                        META_CLASS_NAME: schema_data['title'],
                    },
                ),
                ObjectSchema(**schema_data),
            )
        )

    return schemas


def _get_all_latest_data(
    connection: glue.SqliteConnection | glue.PostgresConnection,
    table_ref: glue.SchemaReference,
) -> Generator[dict[str, Any], None, None]:
    from amsdal_data.connections.historical.data_query_transform import METADATA_FIELD

    is_deleted_field = glue.Field(
        name=METADATA_FIELD,
        child=glue.Field(name='is_deleted'),
    )
    is_deleted_field.child.parent = is_deleted_field  # type: ignore[union-attr]

    conditions = glue.Conditions(
        glue.Condition(
            left=glue.FieldReferenceExpression(
                field_reference=glue.FieldReference(
                    field=glue.Field(name='is_deleted'),
                    table_name=METADATA_TABLE_ALIAS,
                ),
            ),
            lookup=glue.FieldLookup.EQ,
            right=glue.Value(False),
        ),
    )
    if table_ref.name == 'ClassObject':
        conditions.children.append(
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name='meta_class'),
                        table_name=table_ref.name,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                right=glue.Value(value='ClassObject'),
            ),
        )
    _add_latest_condition(conditions)

    _limit = 20
    _offset = 0

    while True:
        limit = glue.LimitQuery(limit=_limit, offset=_offset)

        from amsdal_data.connections.historical.data_query_transform import build_simple_query_statement_with_metadata

        query = build_simple_query_statement_with_metadata(
            table=table_ref,
            where=conditions,
            limit=limit,
        )

        result = connection.query(query)

        if not result:
            break

        for item in result:
            yield item.data

        _offset += _limit
