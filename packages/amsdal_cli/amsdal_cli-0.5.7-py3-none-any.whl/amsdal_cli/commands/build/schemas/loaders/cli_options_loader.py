import logging
from collections.abc import Iterator
from pathlib import Path

from amsdal_cli.commands.build.schemas.data_models.options import OptionSchema
from amsdal_cli.commands.build.schemas.loaders.base import OptionsLoaderBase
from amsdal_cli.commands.build.schemas.loaders.utils import load_object_schema_from_json_file

logger = logging.getLogger(__name__)


class CliOptionsLoader(OptionsLoaderBase):
    """
    Loader for options configuration files in CLI.

    This class is responsible for loading options configuration files from a given configuration directory. It extends
        the `OptionsLoaderBase` to provide methods for iterating over options files and directories.
    """

    def __init__(self, config_dir: Path) -> None:
        self._app_root = config_dir

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._app_root})'

    def iter_options(self) -> Iterator[OptionSchema]:
        """
        Iterates over options configuration files and yields their schemas.

        This method iterates over JSON files in the options directory. For each JSON file, it reads the options from
            the file and yields the schemas.

        Yields:
            Iterator[OptionSchema]: An iterator over the schemas of the options configuration files.
        """
        for json_file in self.iter_json_files():
            yield from self.read_options_from_file(json_file)

    def iter_json_files(self) -> Iterator[Path]:
        """
        Iterates over JSON files in the options directory and yields their paths.

        This method checks if the options directory exists and is a directory. For each item in the directory,
            it checks if the item is a file and has a `.json` extension. If both conditions are met,
            it yields the path to the JSON file.

        Yields:
            Iterator[Path]: An iterator over the paths to the JSON files in the options directory.
        """
        options_dir = self._app_root / 'options'

        if options_dir.exists() and options_dir.is_dir():
            for item in options_dir.iterdir():
                if item.is_file() and item.suffix.lower() == '.json':
                    yield item

    @staticmethod
    def read_options_from_file(json_file: Path) -> Iterator[OptionSchema]:
        """
        Reads options from a JSON file and yields their schemas.

        This method reads the options from the given JSON file and yields the schemas of the options.

        Args:
            json_file (Path): The path to the JSON file containing the options.

        Yields:
            Iterator[OptionSchema]: An iterator over the schemas of the options in the JSON file.
        """
        yield from load_object_schema_from_json_file(json_file, model_cls=OptionSchema)  # type: ignore[misc]
