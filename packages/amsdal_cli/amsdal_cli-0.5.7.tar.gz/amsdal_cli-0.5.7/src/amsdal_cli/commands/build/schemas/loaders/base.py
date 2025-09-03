from abc import ABC
from abc import abstractmethod
from collections.abc import Iterator
from pathlib import Path

from amsdal_utils.schemas.schema import ObjectSchema

from amsdal_cli.commands.build.schemas.data_models.custom_code import CustomCodeSchema
from amsdal_cli.commands.build.schemas.data_models.options import OptionSchema
from amsdal_cli.commands.build.schemas.loaders.utils import load_object_schema_from_json_file


class ConfigLoaderBase(ABC):
    @abstractmethod
    def iter_configs(self) -> Iterator[ObjectSchema]: ...

    @abstractmethod
    def __str__(self) -> str: ...


class OptionsLoaderBase(ABC):
    @abstractmethod
    def iter_options(self) -> Iterator[OptionSchema]: ...

    @abstractmethod
    def __str__(self) -> str: ...


class CustomCodeLoaderBase(ABC):
    @abstractmethod
    def iter_custom_code(self) -> Iterator[CustomCodeSchema]: ...

    @abstractmethod
    def __str__(self) -> str: ...


class TransactionsLoaderBase(ABC):
    @abstractmethod
    def iter_transactions(self) -> Iterator[Path]: ...

    @abstractmethod
    def __str__(self) -> str: ...


class StaticsLoaderBase(ABC):
    @abstractmethod
    def iter_static(self) -> Iterator[Path]: ...

    @abstractmethod
    def __str__(self) -> str: ...


class FixturesLoaderBase(ABC):
    @abstractmethod
    def iter_fixtures(self) -> Iterator[Path]: ...

    @abstractmethod
    def iter_fixture_files(self) -> Iterator[Path]: ...

    @abstractmethod
    def __str__(self) -> str: ...


class ConfigReaderMixin:
    """
    Mixin class for reading configuration files.

    This mixin provides methods to determine if a file is a schema file and to read configurations from a file.
    """

    @classmethod
    def is_schema_file(cls, json_file: Path) -> bool:
        """
        Determines if the given JSON file is a schema file.

        Args:
            json_file (Path): The path to the JSON file.

        Returns:
            bool: True if the file is a schema file, False otherwise.
        """
        object_config = next(cls.read_configs_from_file(json_file))

        return object_config.type != 'Fixture'

    @staticmethod
    def read_configs_from_file(json_file: Path) -> Iterator[ObjectSchema]:
        """
        Reads configurations from the given JSON file.

        Args:
            json_file (Path): The path to the JSON file.

        Yields:
            ObjectSchema: The object schema read from the file.
        """
        yield from load_object_schema_from_json_file(json_file, model_cls=ObjectSchema)  # type: ignore[misc]
