from pathlib import Path

from rich import print as rprint

from amsdal_cli.commands.cloud.environments.constants import DEFAULT_ENV
from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.text import rich_highlight
from amsdal_cli.utils.text import rich_warning


def _get_enviroments_path(cli_config: CliConfig) -> Path:
    config_dir: Path = cli_config.app_directory / '.amsdal'
    config_dir.mkdir(exist_ok=True, parents=True)
    _env_path: Path = config_dir / '.environment'

    if not _env_path.exists():
        _env_path.touch(exist_ok=True)
        set_current_env(cli_config, DEFAULT_ENV)

    return _env_path


def get_current_env(cli_config: CliConfig) -> str:
    _env_path = _get_enviroments_path(cli_config)
    _envs = {env for env in _env_path.read_text().split('\n') if env}

    if len(_envs) == 1:
        return _envs.pop()

    rprint(
        rich_warning(
            'Invalid environment config. Please checkout to a valid environment. '
            f'Using default {rich_highlight(DEFAULT_ENV)} environment.'
        )
    )
    return DEFAULT_ENV


def set_current_env(cli_config: CliConfig, env_name: str) -> None:
    _env_path = _get_enviroments_path(cli_config)

    _env_path.write_text(env_name)
