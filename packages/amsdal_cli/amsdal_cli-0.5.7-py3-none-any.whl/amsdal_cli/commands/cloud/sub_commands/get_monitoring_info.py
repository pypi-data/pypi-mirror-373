import json
import tempfile
import typing
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.table import Table
from typer import Option

from amsdal_cli.commands.cloud.app import cloud_sub_app
from amsdal_cli.commands.cloud.enums import OutputFormat


@cloud_sub_app.command(name='get-monitoring-info, get_monitoring_info, gmi')
def get_monitoring_info(
    ctx: typer.Context,
    env_name: typing.Annotated[
        typing.Optional[str],  # noqa: UP007
        Option('--env', help='Environment name. Default is the current environment from configuration.'),
    ] = None,
    output: Annotated[OutputFormat, typer.Option('--output', '-o')] = OutputFormat.default,
) -> None:
    """
    Retrieves monitoring information for the specified environment.
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

    cli_config: CliConfig = ctx.meta['config']
    env_name = env_name or get_current_env(cli_config)

    if cli_config.verbose:
        rprint(rich_info(f'Retrieving monitoring info for environment: {rich_highlight(env_name)}'))

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
        response = manager.cloud_actions_manager.get_monitoring_info(
            env_name=env_name,
            application_uuid=cli_config.application_uuid,
            application_name=cli_config.application_name,
        )
    except AmsdalCloudError as e:
        rprint(rich_error(str(e)))
        return

    if not response.details:
        rprint('No monitoring info found.')
        return

    if output == OutputFormat.json:
        rprint(json.dumps(response.details.model_dump(), indent=4))
        return

    data_table = Table()
    data_table.add_column('URL', justify='center')
    data_table.add_column('Username', justify='center')
    data_table.add_column('Password', justify='center')

    data_table.add_row(response.details.url, response.details.username, response.details.password)

    rprint(data_table)
