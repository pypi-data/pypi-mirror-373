import tempfile
from pathlib import Path

import typer
from rich import print as rprint

from amsdal_cli.commands.cloud.environments.app import environment_sub_app


@environment_sub_app.command(name='checkout, co')
def environments_checkout(ctx: typer.Context, env_name: str) -> None:
    """
    Changes the current environment to specified one.
    """
    from amsdal.errors import AmsdalCloudError
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_utils.config.manager import AmsdalConfigManager

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.commands.cloud.environments.utils import set_current_env
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_highlight
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_warning
    from amsdal_cli.utils.vcs.base import VCSBaseService

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

    if not list_response.details or not list_response.details.environments:
        rprint(rich_warning('No environments found. Please create one first.'))
        return

    if env_name not in list_response.details.environments:
        rprint(rich_warning(f'Environment {rich_highlight(env_name)} not found.'))
        return

    set_current_env(cli_config, env_name)
    vcs_service: VCSBaseService = ctx.meta['vcs_service']
    vcs_service.checkout(env_name)
    rprint(rich_info(f'Environment changed to {rich_highlight(env_name)}'))
