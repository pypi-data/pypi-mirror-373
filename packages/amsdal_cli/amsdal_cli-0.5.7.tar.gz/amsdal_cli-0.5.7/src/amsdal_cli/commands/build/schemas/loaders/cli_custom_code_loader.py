import logging
from collections.abc import Iterator
from pathlib import Path

from amsdal_utils.schemas.schema import ObjectSchema

from amsdal_cli.commands.build.schemas.data_models.custom_code import CustomCodeSchema
from amsdal_cli.commands.build.schemas.loaders.base import ConfigReaderMixin
from amsdal_cli.commands.build.schemas.loaders.base import CustomCodeLoaderBase

HOOKS = 'hooks'
MODIFIERS = 'modifiers'
PROPERTIES = 'properties'
MODEL_JSON_FILE = 'model.json'

logger = logging.getLogger(__name__)


class CliCustomCodeLoader(ConfigReaderMixin, CustomCodeLoaderBase):
    """
    Loader for custom code in CLI.

    This class is responsible for loading custom code from a given schema directory. It extends the `ConfigReaderMixin`
    and `CustomCodeLoaderBase` to provide methods for iterating over custom code schemas and reading custom code from
    model directories and subdirectories.
    """

    def __init__(self, schema_dir: Path) -> None:
        self._schema_dir = schema_dir

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._schema_dir})'

    def iter_custom_code(self) -> Iterator[CustomCodeSchema]:
        """
        Iterates over custom code schemas.

        This method iterates over model directories and yields custom code schemas that contain code.

        Yields:
            CustomCodeSchema: The custom code schema containing the code.
        """
        for model_directory, object_config in self.iter_model_directories():
            schema = self.read_custom_code_from_model_directory(model_directory, object_config)

            if schema.code:
                yield schema

    def read_custom_code_from_model_directory(
        self,
        model_directory: Path,
        object_config: ObjectSchema,
    ) -> CustomCodeSchema:
        """
        Reads custom code from a model directory.

        This method reads custom code from the specified model directory by iterating over predefined subdirectories
        (hooks, modifiers, properties) and collecting Python code files.

        Args:
            model_directory (Path): The path to the model directory.
            object_config (ObjectSchema): The object schema configuration.

        Returns:
            CustomCodeSchema: The custom code schema containing the collected code.
        """
        code_parts: list[str] = []

        for subdirectory in (HOOKS, MODIFIERS, PROPERTIES):
            code_parts.extend(self.read_custom_code_from_subdirectory(model_directory, subdirectory))

        return CustomCodeSchema(
            name=object_config.title,
            code='\n\n'.join(code_parts),
        )

    def read_custom_code_from_subdirectory(self, model_directory: Path, subdirectory: str) -> list[str]:
        """
        Reads custom code from a subdirectory.

        This method reads Python code files from the specified subdirectory within the model directory. It collects the
        content of these files and returns them as a list of strings.

        Args:
            model_directory (Path): The path to the model directory.
            subdirectory (str): The name of the subdirectory to read code from.

        Returns:
            list[str]: A list of strings containing the content of the Python code files.
        """
        hooks_dir = model_directory / subdirectory
        code_parts: list[tuple[str, str]] = []

        if not hooks_dir.exists():
            return []

        for item in hooks_dir.iterdir():
            if not item.is_file() or item.suffix.lower() != '.py':
                continue

            if content := item.read_text('utf-8'):
                code_parts.append((item.name, content.strip()))

        return [item[1] for item in sorted(code_parts, key=lambda _item: _item[0])]

    def iter_model_directories(self) -> Iterator[tuple[Path, ObjectSchema]]:
        """
        Iterates over model directories.

        This method iterates over directories within the schema directory, checking if they contain a valid model
            JSON file.
        If a valid model JSON file is found, it yields the directory path and the corresponding object schema.

        Yields:
            tuple[Path, ObjectSchema]: A tuple containing the path to the model directory and the object schema.
        """
        if self._schema_dir.exists():
            for item in self._schema_dir.iterdir():
                if item.is_dir() and (item / MODEL_JSON_FILE).exists() and self.is_schema_file(item / MODEL_JSON_FILE):
                    yield item, next(self.read_configs_from_file(item / MODEL_JSON_FILE))
