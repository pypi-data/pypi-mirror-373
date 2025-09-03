import json
from pathlib import Path

import typer
from rich import print as rprint

from amsdal_cli.commands.generate.app import sub_app


@sub_app.command(name='frontend_config, fconfig, fcfg, fc')
def generate_frontend_config(
    ctx: typer.Context,
    model: str = typer.Option(..., help='The model name. It should be provided in PascalCase.'),
) -> None:
    """
    Generates Frontend Config fixture file for the specified model.
    """
    from amsdal.contrib.frontend_configs.lifecycle.consumer import get_default_control
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_utils.config.manager import AmsdalConfigManager
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.commands.generate.enums import FIXTURES
    from amsdal_cli.commands.generate.utils.build_base_path import build_model_base_path
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.copier import write_file
    from amsdal_cli.utils.text import rich_error

    cli_config: CliConfig = ctx.meta['config']
    config_manager = AmsdalConfigManager()
    config_manager.load_config(cli_config.config_path)
    amsdal_manager: AsyncAmsdalManager | AmsdalManager

    if config_manager.get_config().async_mode:
        amsdal_manager = AsyncAmsdalManager()
    else:
        amsdal_manager = AmsdalManager()

    amsdal_manager.pre_setup()

    try:
        target_fixture = {
            'FrontendModelConfig': [
                {
                    'external_id': f'{to_snake_case(model)}_frontend_config',
                    'class_name': model,
                    'control': get_default_control(model),
                }
            ]
        }
    except ModuleNotFoundError as e:
        rprint(rich_error(f'Model {model} not found. Please consider building the app first.'))
        raise typer.Exit from e

    base_path = build_model_base_path(ctx, model)

    (base_path / FIXTURES).mkdir(parents=True, exist_ok=True)
    frontend_config_file = base_path / FIXTURES / 'ui.json'
    current_dir = Path('.').absolute()

    if frontend_config_file.exists():
        owerrite = input(
            f'The file "{frontend_config_file.relative_to(current_dir)}" already exists. '
            'Would you like to overwrite it? [y/N]: '
        ).strip()

        if owerrite.lower() != 'y':
            return

    write_file(
        json.dumps(target_fixture, indent=cli_config.indent),
        destination_file_path=frontend_config_file,
        confirm_overwriting=False,
    )
