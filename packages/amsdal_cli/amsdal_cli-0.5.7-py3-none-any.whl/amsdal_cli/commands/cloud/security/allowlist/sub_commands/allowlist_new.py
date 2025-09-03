import tempfile
import typing
from pathlib import Path
from typing import Annotated
from typing import Optional

import typer
from rich import print as rprint
from typer import Option

from amsdal_cli.commands.cloud.security.allowlist.app import allowlist_sub_app


@allowlist_sub_app.command(name='new, n')
def new_allowlist_ip_command(
    ctx: typer.Context,
    env_name: typing.Annotated[
        typing.Optional[str],  # noqa: UP007
        Option('--env', help='Environment name. Default is the current environment from configuration.'),
    ] = None,
    *,
    ip_address: Annotated[
        Optional[str],  # noqa: UP007
        typer.Option(
            '--ip-address',
            help='IP address, range or combination of both to add to the allowlist. Will add your IP if not provided.',
        ),
    ] = None,
) -> None:
    """
    Adds your IP to the allowlist of the API.

    Examples of usage:

    ```bash
    amsdal cloud security allowlist new
    amsdal cloud security allowlist new --ip-address 0.0.0.0
    amsdal cloud security allowlist new --ip-address 0.0.0.0/24
    amsdal cloud security allowlist new --ip-address 0.0.0.0,1.0.0.0/24
    ```
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
    from amsdal_cli.utils.text import rich_success

    cli_config: CliConfig = ctx.meta['config']
    env_name = env_name or get_current_env(cli_config)

    if cli_config.verbose:
        rprint(rich_info(f'Adding IP address/range to the allowlist for environment: {rich_highlight(env_name)}'))

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
        manager.cloud_actions_manager.add_allowlist_ip(
            env_name=env_name,
            application_uuid=cli_config.application_uuid,
            application_name=cli_config.application_name,
            ip_address=ip_address,
        )
    except AmsdalCloudError as e:
        rprint(rich_error(str(e)))
        return

    if ip_address:
        msg = (
            f'IP address/range {rich_success(ip_address)} has been added to the allowlist. '
            'Rules should be applied in a few minutes.'
        )
    else:
        msg = 'Your IP address has been added to the allowlist. Rules should be applied in a few minutes.'

    rprint(msg)
