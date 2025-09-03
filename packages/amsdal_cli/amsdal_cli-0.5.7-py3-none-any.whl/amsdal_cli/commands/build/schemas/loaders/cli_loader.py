from collections.abc import Iterator
from pathlib import Path

from amsdal_utils.schemas.schema import ObjectSchema

from amsdal_cli.commands.build.schemas.loaders.base import ConfigLoaderBase
from amsdal_cli.commands.build.schemas.loaders.base import ConfigReaderMixin

MODEL_JSON_FILE = 'model.json'


class CliConfigLoader(ConfigReaderMixin, ConfigLoaderBase):
    """
    Loader for configuration files in CLI.

    This class is responsible for loading configuration files from a given configuration directory. It extends the
    `ConfigReaderMixin` and `ConfigLoaderBase` to provide methods for iterating over configuration files and directories
    """

    def __init__(self, config_dir: Path) -> None:
        self._config_dir = config_dir

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._config_dir})'

    def iter_configs(self) -> Iterator[ObjectSchema]:
        """
        Iterates over configuration files and yields their schemas.

        This method iterates over JSON files in the configuration directory. For each JSON file,
            it checks if the file is a schema file.
            If it is, it reads the configurations from the file and yields the schemas.

        Yields:
            Iterator[ObjectSchema]: An iterator over the schemas of the configuration files.
        """
        for json_file in self.iter_json_files():
            if self.is_schema_file(json_file):
                yield from self.read_configs_from_file(json_file)

    def iter_json_files(self) -> Iterator[Path]:
        """
        Iterates over JSON files in the configuration directory and yields their paths.

        This method checks if the configuration directory exists. For each item in the directory,
            it checks if the item is a directory and contains a model JSON file. If both conditions are met,
            it yields the path to the model JSON file.

        Yields:
            Iterator[Path]: An iterator over the paths to the JSON files in the configuration directory.
        """
        if self._config_dir.exists():
            for item in self._config_dir.iterdir():
                if item.is_dir() and (item / MODEL_JSON_FILE).exists():
                    yield item / MODEL_JSON_FILE
