import tempfile
import traceback
from pathlib import Path

import typer
from rich import print as rprint

from amsdal_cli.app import app


@app.command(name='verify, vrf, v')
def verify_command(
    ctx: typer.Context,
    *,
    building: bool = typer.Option(False, help='Do verify model building?'),
) -> None:
    """
    Verifies all application's files such as models, properties, transactions, etc.
    """

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.commands.generate.enums import MODEL_JSON_FILE
    from amsdal_cli.commands.verify.utils.verify_json_model import verify_json_model
    from amsdal_cli.commands.verify.utils.verify_python_file import verify_python_file
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.copier import walk
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    cli_config: CliConfig = ctx.meta['config']
    errors = []

    rprint(rich_info('Syntax checking...'), end=' ')

    for file_item in walk(cli_config.app_directory / cli_config.src_dir):
        if file_item.name == MODEL_JSON_FILE:
            errors.extend(verify_json_model(file_item))
        elif file_item.name.endswith('.py'):
            errors.extend(verify_python_file(file_item))

    if errors:
        for error in errors:
            rprint(rich_error(f'File: {error.file_path.resolve()}: {error.message}'))
            rprint(rich_error(str(error.details)))

        raise typer.Exit(1)

    rprint(rich_success('OK!'))

    if not building:
        return

    rprint(rich_info('Build models checking...'), end=' ')
    with tempfile.TemporaryDirectory() as _temp_dir:
        output_path: Path = Path(_temp_dir)

        app_builder = AppBuilder(
            cli_config=cli_config,
            config_path=cli_config.config_path,
        )

        try:
            app_builder.build(output_path, is_silent=True)
        except Exception as ex:
            rprint(rich_error(f'Failed: {ex} - {traceback.format_exc()}'))
            raise typer.Exit(1) from ex

    rprint(rich_success('OK!'))
