import importlib
from types import ModuleType
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeAlias

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    COMMANDS: list[str | ModuleType] = Field(
        default=[
            'amsdal_cli.commands.api_check',
            'amsdal_cli.commands.new',
            'amsdal_cli.commands.plugin',
            'amsdal_cli.commands.generate',
            'amsdal_cli.commands.verify',
            'amsdal_cli.commands.build',
            'amsdal_cli.commands.clean',
            'amsdal_cli.commands.serve',
            'amsdal_cli.commands.restore',
            'amsdal_cli.commands.cloud',
            'amsdal_cli.commands.migrations',
            'amsdal_cli.commands.ci_cd',
            'amsdal_cli.commands.tests',
            'amsdal_cli.commands.worker',
            'amsdal_cli.commands.register_connection',
        ]
    )

    CHECK_AMSDAL_VERSIONS: bool = True
    """If True, the latest version of the amsdal modules will be checked and displayed."""
    AMSDAL_APPLICATION_UUID: str | None = None
    """The UUID of the application."""

    @field_validator('COMMANDS')
    @classmethod
    def load_commands(cls, value: list[Any]) -> list[ModuleType]:
        commands: list[ModuleType] = []

        for module in value:
            if isinstance(module, str):
                commands.append(importlib.import_module(f'{module}.command'))

        return commands


if TYPE_CHECKING:
    base: TypeAlias = Settings
else:
    base: TypeAlias = object


class SettingsProxy(base):
    def __init__(self) -> None:
        self._settings = Settings()

    def override(self, **kwargs: Any) -> None:
        new_settings = self._settings.model_dump()
        new_settings.update(kwargs)
        self._settings = Settings(**new_settings)

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._settings.model_dump(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._settings, name)

    def __delattr__(self, name: str) -> None:
        try:
            getattr(self._settings, name)
            self._settings.__delattr__(name)
        except AttributeError:
            msg = f'Settings object has no attribute {name}'
            raise AttributeError(msg) from None

    def __setattr__(self, name: str, value: Any) -> None:
        if name == '_settings':
            super().__setattr__(name, value)
            return

        self._settings.__setattr__(name, value)


settings: SettingsProxy = SettingsProxy()
