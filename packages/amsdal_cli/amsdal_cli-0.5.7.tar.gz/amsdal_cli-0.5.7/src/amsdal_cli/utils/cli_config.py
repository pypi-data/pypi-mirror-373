import re
from enum import Enum
from pathlib import Path

from pydantic import BaseModel
from pydantic import model_validator

from amsdal_cli.utils.vcs.enums import VCSOptions

APPLICATION_UUID_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9]{31}$')


class ModelsFormat(str, Enum):
    JSON = 'json'
    PY = 'py'


class CliConfig(BaseModel):
    """
    Configuration class for the AMSDAL CLI.

    Attributes:
        templates_path (Path): Path to the templates' directory.
        config_path (Path): Path to the configuration file. Defaults to '/dev/null'.
        http_port (int): HTTP port number. Defaults to 8080.
        check_model_exists (bool): Flag to check if the model exists. Defaults to True.
        application_uuid (str | None): UUID of the application. Defaults to None.
        application_name (str | None): Name of the application. Defaults to None.
        models_format (ModelsFormat): Format of models are used in this app.
        indent (int): Indentation level for JSON output. Defaults to 4.
        app_directory (Path): Path to the application directory. Defaults to '/dev/null'.
        verbose (bool): Flag to enable verbose output. Defaults to True.
        vcs (VCSOptions | None): Version control system options. Defaults to None.
    """

    templates_path: Path
    config_path: Path = Path('/dev/null')
    http_port: int = 8080
    check_model_exists: bool = True
    application_uuid: str | None = None
    application_name: str | None = None
    models_format: ModelsFormat = ModelsFormat.PY
    indent: int = 4
    app_directory: Path = Path('/dev/null')
    verbose: bool = True
    is_plugin: bool = False
    vcs: VCSOptions | None = None
    src_dir: str = 'src'

    @model_validator(mode='after')
    def validate_config_path(self) -> 'CliConfig':
        """
        Validate the configuration path and application UUID.

        Returns:
           CliConfig: The validated configuration object.

        Raises:
           ValueError: If the application UUID does not match the pattern or the configuration path does not exist.
        """
        if self.app_directory == Path('/dev/null'):
            return self

        full_config_path: Path = self.app_directory / self.config_path
        self.config_path = full_config_path

        if self.application_uuid and not APPLICATION_UUID_PATTERN.match(self.application_uuid):
            msg = (
                f'The application_uuid "{self.application_uuid}" should match the '
                f'pattern "{APPLICATION_UUID_PATTERN.pattern}".'
            )
            raise ValueError(msg)

        if not full_config_path.exists():
            msg = f'The "{full_config_path}" does not exists. Check ".amdsal-cli -> config_path".'
            raise ValueError(msg)

        return self
