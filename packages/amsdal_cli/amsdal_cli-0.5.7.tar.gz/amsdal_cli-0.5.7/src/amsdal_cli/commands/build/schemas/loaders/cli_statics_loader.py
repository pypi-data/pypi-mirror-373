from collections.abc import Iterator
from pathlib import Path

from amsdal_cli.commands.build.schemas.loaders.base import StaticsLoaderBase


class CliStaticsLoader(StaticsLoaderBase):
    """
    Loader for static files in CLI.

    This class is responsible for loading static files from a given application root directory. It extends the
    `StaticsLoaderBase` to provide methods for iterating over static files.
    """

    def __init__(self, app_root: Path) -> None:
        self._app_root = app_root

    def iter_static(self) -> Iterator[Path]:
        """
        Iterates over static files and yields their paths.

        This method checks if the static directory exists and is a directory. For each item in the directory,
            it checks if the item is a file. If the condition is met, it yields the path to the static file.

        Yields:
            Iterator[Path]: An iterator over the paths to the static files in the static directory.
        """
        _static_path = self._app_root / 'static'

        if _static_path.exists() and _static_path.is_dir():
            for internal_path in _static_path.iterdir():
                if internal_path.is_file():
                    yield internal_path

    def __str__(self) -> str:
        return f'{self.__class__.__name__}'
