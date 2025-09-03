import json
import tempfile
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.table import Table

from amsdal_cli.commands.cloud.enums import OutputFormat
from amsdal_cli.commands.cloud.environments.app import environment_sub_app


@environment_sub_app.callback(invoke_without_command=True)
def environments_list_callback(
    ctx: typer.Context,
    output: Annotated[OutputFormat, typer.Option('--output', '-o')] = OutputFormat.default,
) -> None:
    """
    Lists the environments of the Cloud Server app.
    """
    from amsdal.errors import AmsdalCloudError
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_utils.config.manager import AmsdalConfigManager

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.commands.cloud.environments.utils import get_current_env
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_highlight
    from amsdal_cli.utils.text import rich_info

    if ctx.invoked_subcommand is not None:
        return

    cli_config: CliConfig = ctx.meta['config']

    with tempfile.TemporaryDirectory() as _temp_dir:
        output_path: Path = Path(_temp_dir)
        app_builder = AppBuilder(
            cli_config=cli_config,
            config_path=cli_config.config_path,
        )
        app_builder.build(output_path, is_silent=True)
        manager: AsyncAmsdalManager | AmsdalManager

        manager = AsyncAmsdalManager() if AmsdalConfigManager().get_config().async_mode else AmsdalManager()

        manager.authenticate()

    try:
        list_response = manager.cloud_actions_manager.list_envs(
            application_uuid=cli_config.application_uuid,
            application_name=cli_config.application_name,
        )
    except AmsdalCloudError as e:
        rprint(rich_error(str(e)))
        raise typer.Exit(1) from e

    if not list_response:
        return
    current_env_name = get_current_env(cli_config)

    if output == OutputFormat.json:
        if cli_config.verbose:
            rprint(rich_info(f'Current environment: {rich_highlight(current_env_name)}'))

        rprint(json.dumps(list_response.model_dump(), indent=4))

        return

    if not list_response.details or not list_response.details.environments:
        rprint(rich_info('No environments found.'))

        return

    data_table = Table()
    data_table.add_column('Environment', justify='center')
    data_table.add_column('Current', justify='center')

    for env in list_response.details.environments:
        data_table.add_row(env, '*' if current_env_name == env else '')

    rprint(data_table)
