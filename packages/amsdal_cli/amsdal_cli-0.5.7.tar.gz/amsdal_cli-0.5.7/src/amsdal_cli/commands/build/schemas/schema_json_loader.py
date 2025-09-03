from collections.abc import Iterator
from itertools import chain
from pathlib import Path
from typing import TypeAlias

from amsdal_utils.schemas.interfaces import BaseDependsSchemaLoader
from amsdal_utils.schemas.interfaces import BaseSchemaLoader
from amsdal_utils.schemas.schema import ObjectSchema

from amsdal_cli.commands.build.schemas.data_models.schemas_directory import SchemasDirectory
from amsdal_cli.commands.build.schemas.extenders.custom_code_extender import CustomCodeExtender
from amsdal_cli.commands.build.schemas.extenders.options_extender import OptionsExtender
from amsdal_cli.commands.build.schemas.loaders.cli_custom_code_loader import CliCustomCodeLoader
from amsdal_cli.commands.build.schemas.loaders.cli_loader import CliConfigLoader
from amsdal_cli.commands.build.schemas.loaders.cli_options_loader import CliOptionsLoader
from amsdal_cli.commands.build.schemas.mixins.enrich_schemas_mixin import EnrichSchemasMixin

ModulePathType: TypeAlias = str


class LoadSchemaMixin:
    @staticmethod
    def load_schemas_from_path(schemas_path: Path) -> Iterator[ObjectSchema]:
        """
        Loads schemas from the specified path.

        This method reads schemas from the given path and returns an iterator of `ObjectSchema` objects. It uses various
        loaders and extenders to process the schemas.

        Args:
            schemas_path (Path): The path from which to load the schemas.

        Returns:
            Iterator[ObjectSchema]: An iterator of `ObjectSchema` objects.
        """
        schema_reader = CliConfigLoader(schemas_path)
        options_reader = CliOptionsLoader(schemas_path.parent)
        options_extender = OptionsExtender(options_reader)
        custom_code_reader = CliCustomCodeLoader(schemas_path)
        custom_code_extender = CustomCodeExtender(custom_code_reader)

        for object_schema in schema_reader.iter_configs():
            options_extender.extend(object_schema)
            custom_code_extender.extend(object_schema)

            yield object_schema

        options_extender.post_extend()
        custom_code_extender.post_extend()


class SimpleSchemaJsonLoader(LoadSchemaMixin, BaseSchemaLoader):
    def __init__(self, schema_directory: SchemasDirectory) -> None:
        self._schema_directory = schema_directory
        self._schemas_per_module: dict[ModulePathType, list[ObjectSchema]] = {}
        super().__init__()

    @property
    def schemas_per_module(self) -> dict[ModulePathType, list[ObjectSchema]]:
        return self._schemas_per_module

    def load(self) -> list[ObjectSchema]:
        _schemas = list(self.load_schemas_from_path(self._schema_directory.path))
        self._schemas_per_module[self._schema_directory.module_path] = _schemas

        return _schemas


class SchemaJsonLoader(LoadSchemaMixin, EnrichSchemasMixin, BaseDependsSchemaLoader):
    def __init__(self, schema_directory: SchemasDirectory) -> None:
        self._schema_directory = schema_directory
        self._schemas_per_module: dict[ModulePathType, list[ObjectSchema]] = {}
        super().__init__()

    @property
    def schemas_per_module(self) -> dict[ModulePathType, list[ObjectSchema]]:
        return self._schemas_per_module

    def load(self, type_schemas: list[ObjectSchema], *extra_schemas: list[ObjectSchema]) -> list[ObjectSchema]:
        _schemas = list(self.load_schemas_from_path(self._schema_directory.path))
        _schemas = self._enrich(type_schemas, _schemas, extra_schemas=chain.from_iterable(extra_schemas))
        self._schemas_per_module[self._schema_directory.module_path] = _schemas
        return _schemas


class SchemaMultiDirectoryJsonLoader(LoadSchemaMixin, EnrichSchemasMixin, BaseDependsSchemaLoader):
    def __init__(self, schema_directories: list[SchemasDirectory]) -> None:
        self._schema_directories = schema_directories
        self._schemas_per_module: dict[ModulePathType, list[ObjectSchema]] = {}
        super().__init__()

    @property
    def schemas_per_module(self) -> dict[ModulePathType, list[ObjectSchema]]:
        return self._schemas_per_module

    def load(self, type_schemas: list[ObjectSchema], *extra_schemas: list[ObjectSchema]) -> list[ObjectSchema]:
        all_schemas = []
        _extra_schemas: list[ObjectSchema] = list(chain.from_iterable(extra_schemas))

        for _directory in self._schema_directories:
            _schemas = list(self.load_schemas_from_path(_directory.path))
            _enriched_schemas = self._enrich(type_schemas, _schemas, extra_schemas=chain.from_iterable(extra_schemas))
            all_schemas.extend(_enriched_schemas)
            _extra_schemas.extend(_enriched_schemas)
            self._schemas_per_module[_directory.module_path] = _enriched_schemas

        return all_schemas
