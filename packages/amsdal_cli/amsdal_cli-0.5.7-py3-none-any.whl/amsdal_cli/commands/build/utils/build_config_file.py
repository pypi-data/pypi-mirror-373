from pathlib import Path

import typer
from rich import print as rprint

from amsdal_cli.utils.text import CustomConfirm
from amsdal_cli.utils.text import rich_error
from amsdal_cli.utils.text import rich_info
from amsdal_cli.utils.text import rich_success


def build_config_file(
    output_path: Path,
    config_path: Path,
    *,
    no_input: bool,
    is_silent: bool = False,
) -> None:
    """
    Builds the config.yml file from the given configuration path to the output path.

    Args:
        output_path (Path): The directory where the config.yml file will be created.
        config_path (Path): The path to the source configuration file.
        no_input (bool): If True, the function will not prompt for user input and will overwrite existing files.
        is_silent (bool, optional): If True, the function will not print any output. Defaults to False.

    Returns:
        None
    """
    if not is_silent:
        rprint(rich_info('Building config.yml file...'), end=' ')

    if not config_path.exists() or not config_path.name.endswith('.yml'):
        if not is_silent:
            rprint(rich_error(f'\nConfig file "{config_path.resolve()}" does not exist or has wrong extension.'))
        raise typer.Exit(1)

    config_destination = output_path / 'config.yml'

    if (
        no_input
        or not config_destination.exists()
        or (
            CustomConfirm.ask(
                rich_info(
                    f'\nThe config file "{config_destination.resolve()}" already exists. '
                    'Would you like to overwrite it?'
                ),
                default=False,
                show_default=False,
                choices=['y', 'N'],
            )
        )
    ):
        config_destination.parent.mkdir(parents=True, exist_ok=True)
        config_destination.touch(exist_ok=True)

        with config_path.open('rt') as _file:
            config_destination.write_text(_file.read())

    if not is_silent:
        rprint(rich_success('OK!'))
