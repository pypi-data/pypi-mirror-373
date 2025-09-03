import sys
from datetime import date
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from amsdal_cli.utils.cli_config import ModelsFormat

if TYPE_CHECKING:
    from amsdal_cli.utils.cli_config import CliConfig


class ModelGenerator:
    _cached_schemas = None

    def __init__(
        self,
        config_path: Path,
        meta: dict[str, dict[str, Any]],
        output_dir: Path,
        models_format: ModelsFormat,
    ) -> None:
        self._config_path = config_path
        self._meta = meta
        self._output_dir = output_dir
        self._models_format = models_format

    @classmethod
    def fetch_schemas(cls, connection_name: str) -> list[Any]:
        if cls._cached_schemas is None:
            import amsdal_glue as glue
            from amsdal_data.utils import resolve_backend_class
            from amsdal_utils.config.manager import AmsdalConfigManager

            config_manager = AmsdalConfigManager()
            config = config_manager.get_config()
            connection_config = config.connections[connection_name]
            connection_class = resolve_backend_class(connection_config.backend)
            connection_pool = glue.DefaultConnectionPool(
                connection_class,  # type: ignore[arg-type]
                **connection_config.credentials,
            )
            connection = connection_pool.get_connection()
            cls._cached_schemas = connection.query_schema()

        return cls._cached_schemas

    @classmethod
    async def async_fetch_schemas(cls, connection_name: str) -> list[Any]:
        if cls._cached_schemas is None:
            import amsdal_glue as glue
            from amsdal_data.utils import resolve_backend_class
            from amsdal_utils.config.manager import AmsdalConfigManager

            config_manager = AmsdalConfigManager()
            config = config_manager.get_config()
            connection_config = config.connections[connection_name]
            connection_class = resolve_backend_class(connection_config.backend)
            connection_pool = glue.DefaultAsyncConnectionPool(
                connection_class,  # type: ignore[arg-type]
                **connection_config.credentials,
            )
            connection = await connection_pool.get_connection()
            cls._cached_schemas = await connection.query_schema()
        return cls._cached_schemas

    def generate(self, connection_name: str, cli_config: 'CliConfig') -> None:
        from amsdal.configs.main import settings
        from amsdal_models.builder.services.class_builder import ClassBuilder
        from amsdal_utils.models.enums import ModuleType
        from amsdal_utils.utils.text import to_snake_case

        from amsdal_cli.utils.schema_repository import build_schema_repository

        schemas = self.fetch_schemas(connection_name)
        object_schemas = [self.glue_schema_to_object_schema(schema) for schema in schemas]

        if self._models_format == ModelsFormat.JSON:
            for object_schema, _ in object_schemas:
                class_name = object_schema.title
                model_path = self._output_dir / to_snake_case(class_name) / 'model.json'
                model_path.parent.mkdir(exist_ok=True, parents=True)
                model_path.write_text(
                    object_schema.model_dump_json(
                        indent=cli_config.indent,
                        exclude_none=True,
                        exclude={'meta_class'},
                    ),
                )
        else:
            output_path = self._output_dir
            output_path.mkdir(exist_ok=True, parents=True)
            (output_path / '__init__.py').touch(exist_ok=True)

            sys.path.insert(0, str(output_path.absolute()))

            class_builder = ClassBuilder()
            schema_repository = build_schema_repository(cli_config=cli_config, skip_user_models=True)
            model_module_info = schema_repository.model_module_info

            for object_schema, deps in object_schemas:
                for dependency in deps:
                    model_module_info._info[ModuleType.USER][dependency] = settings.USER_MODELS_MODULE

                if object_schema.title == 'Grades':
                    pass
                class_builder.build(
                    models_package_path=output_path,
                    models_module_path=settings.USER_MODELS_MODULE,
                    object_schema=object_schema,
                    module_type=ModuleType.USER,
                    dependencies=model_module_info,  # type: ignore[arg-type]
                    indent_width=' ' * cli_config.indent,
                )

    def glue_schema_to_object_schema(self, glue_schema: Any) -> tuple[Any, list[str]]:
        import amsdal_glue as glue
        from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
        from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
        from amsdal_data.utils import INDEXED_PROPERTY
        from amsdal_data.utils import PRIMARY_KEY_PROPERTY
        from amsdal_data.utils import TABLE_NAME_PROPERTY
        from amsdal_data.utils import UNIQUE_PROPERTY
        from amsdal_utils.schemas.schema import ObjectSchema
        from amsdal_utils.utils.text import classify
        from amsdal_utils.utils.text import to_snake_case

        properties = {}
        required_fields = []
        unique_constraints = []
        indexed_fields = []
        depends = []
        fk_counter: dict[str, int] = {}

        # Extract primary key fields from constraints
        pk_fields = []
        for constraint in glue_schema.constraints or []:
            if isinstance(constraint, glue.PrimaryKeyConstraint):
                pk_fields = constraint.fields
                break

        # Process properties
        for prop in glue_schema.properties:
            # Skip partition keys as they're handled separately
            if prop.name in (PRIMARY_PARTITION_KEY, SECONDARY_PARTITION_KEY):
                continue

            # Convert property to ObjectSchema format
            property_data = {
                'type': self.glue_type_to_object_schema_type(prop.type),
                'title': prop.name,
            }

            if prop.default is not None:
                property_data['default'] = prop.default

            properties[prop.name] = property_data

            if prop.required:
                required_fields.append(prop.name)

        # Process foreign key constraints
        if glue_schema.constraints:
            for constraint in glue_schema.constraints:
                if isinstance(constraint, glue.ForeignKeyConstraint):
                    ref_table = constraint.reference_schema.name
                    ref_class_name = classify(ref_table)
                    _counter = fk_counter.setdefault(ref_table, 0)
                    fk_counter[ref_table] = _counter + 1

                    _field_name = to_snake_case(ref_table)

                    if _counter > 0:
                        _field_name += f'_{_counter}'

                    _is_required = True

                    for _field in constraint.fields:
                        _is_required = _is_required and _field in required_fields
                        properties.pop(_field, None)

                    required_fields = [f for f in required_fields if f not in constraint.fields]
                    properties[_field_name] = {
                        'type': ref_class_name,
                        'title': _field_name,
                        'db_field': constraint.fields,
                    }

                    pk_fields = self.replace_list_subset(
                        pk_fields,
                        constraint.fields,
                        [_field_name],
                    )

                    if _is_required:
                        required_fields.append(_field_name)

                    depends.append(ref_class_name)
                elif isinstance(constraint, glue.UniqueConstraint):
                    unique_constraints.append(constraint.fields)

        # Process indexes
        if glue_schema.indexes:
            for index in glue_schema.indexes:
                indexed_fields.extend(index.fields)

        # Create the ObjectSchema
        schema_data = {
            'title': classify(glue_schema.name),
            TABLE_NAME_PROPERTY: glue_schema.name,  # Set both title and table_name to the glue schema name
            'properties': properties,
            'required': required_fields,
        }

        if self._meta:
            for _file_name in self._meta:
                _file_path = Path(_file_name)

                if _file_path.stem == glue_schema.name:
                    _file_meta = self._meta[_file_name]

                    pk_fields.extend(_file_meta.get('pk', []))
                    break

        # Add metadata properties
        if pk_fields:
            schema_data[PRIMARY_KEY_PROPERTY] = pk_fields
        if unique_constraints:
            schema_data[UNIQUE_PROPERTY] = unique_constraints
        if indexed_fields:
            schema_data[INDEXED_PROPERTY] = indexed_fields

        return ObjectSchema(**schema_data), depends

    @staticmethod
    def glue_type_to_object_schema_type(glue_type: type) -> str:
        """Converts Glue type to ObjectSchema type, reverse of object_schema_type_to_glue_type."""
        from amsdal_utils.models.data_models.enums import CoreTypes

        type_mapping = {
            dict: CoreTypes.DICTIONARY.value,
            float: CoreTypes.NUMBER.value,
            int: CoreTypes.INTEGER.value,
            bool: CoreTypes.BOOLEAN.value,
            str: CoreTypes.STRING.value,
            date: CoreTypes.DATE.value,
            datetime: CoreTypes.DATETIME.value,
            bytes: CoreTypes.BINARY.value,
            list: CoreTypes.ARRAY.value,
        }
        return type_mapping.get(glue_type, CoreTypes.STRING.value)

    @staticmethod
    def get_properties_by_names(schema: Any, names: list[str]) -> list[Any]:
        """Helper function to get property schemas by their names."""
        return [next(p for p in schema.properties if p.name == name) for name in names]

    @staticmethod
    def replace_list_subset(
        target: list[str],
        subset: list[str],
        replacement: list[str],
    ) -> list[str]:
        if not subset:
            return target.copy()

        subset_len = len(subset)

        # Check if all items in subset exist in target and in the same order
        for i in range(len(target) - subset_len + 1):
            if target[i : i + subset_len] == subset:
                # Create a new list with the replacement
                return target[:i] + replacement + target[i + subset_len :]

        return target.copy()
