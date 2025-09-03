from pathlib import Path

import typer
from rich import print as rprint

from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.text import rich_error


def build_model_base_path(ctx: typer.Context, model_name: str) -> Path:
    """
    Builds the base path for the specified model.

    Args:
        ctx (typer.Context): The Typer context object.
        model_name (str): The name of the model.

    Returns:
        Path: The base path for the specified model.
    """
    from amsdal_utils.utils.text import to_snake_case

    cli_config: CliConfig = ctx.meta['config']
    model = to_snake_case(model_name)
    model_path = cli_config.app_directory / cli_config.src_dir / 'models' / model

    if cli_config.check_model_exists and not (
        (model_path / 'model.json').exists() or (model_path / 'model.py').exists()
    ):
        rprint(rich_error(f'The model "{model_name}" does not exist.'))
        raise typer.Exit

    return model_path
