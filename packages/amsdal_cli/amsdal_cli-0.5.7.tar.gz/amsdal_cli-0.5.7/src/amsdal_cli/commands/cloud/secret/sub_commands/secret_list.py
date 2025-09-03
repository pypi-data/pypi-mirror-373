import json
import tempfile
import typing
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.table import Table
from typer import Option

from amsdal_cli.commands.cloud.enums import OutputFormat
from amsdal_cli.commands.cloud.secret.app import secret_sub_app


def secret_list_command(
    ctx: typer.Context,
    output: Annotated[OutputFormat, typer.Option('--output', '-o')] = OutputFormat.default,
    env_name: typing.Annotated[
        typing.Optional[str],  # noqa: UP007
        Option('--env', help='Environment name. Default is the current environment from configuration.'),
    ] = None,
    *,
    values: Annotated[bool, typer.Option('--values', '-v', help='Show secret values')] = False,
    sync: bool = Option(
        False,
        '--sync',
        help='Sync the dependencies from the Cloud Server to ".secrets".',
    ),
) -> None:
    """
    List the app secrets on the Cloud Server.

    Args:
        ctx (typer.Context): The Typer context object.
        output (Annotated[OutputFormat, typer.Option]): The output format for the list.
            Defaults to OutputFormat.default.
        env_name (typing.Annotated[typing.Optional[str], Option]): The name of the environment. Defaults to the current
            environment from configuration.
        values (Annotated[bool, typer.Option]): Whether to show secret values. Defaults to False.
        sync (bool): Whether to sync the dependencies from the Cloud Server to ".secrets". Defaults to False.

    Returns:
        None
    """
    from amsdal.errors import AmsdalCloudError
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_utils.config.manager import AmsdalConfigManager

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.commands.cloud.environments.utils import get_current_env
    from amsdal_cli.commands.cloud.secret.constants import DEFAULT_SECRETS
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_highlight
    from amsdal_cli.utils.text import rich_info

    cli_config: CliConfig = ctx.meta['config']
    env_name = env_name or get_current_env(cli_config)

    if cli_config.verbose:
        rprint(rich_info(f'Listing secrets for environment: {rich_highlight(env_name)}'))

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
        list_response = manager.cloud_actions_manager.list_secrets(
            with_values=values,
            env_name=env_name,
            application_uuid=cli_config.application_uuid,
            application_name=cli_config.application_name,
        )
    except AmsdalCloudError as e:
        rprint(rich_error(str(e)))
        raise typer.Exit(1) from e

    if not list_response:
        return

    if sync:
        config_dir: Path = cli_config.app_directory / '.amsdal'
        config_dir.mkdir(exist_ok=True, parents=True)
        _secrets_path: Path = config_dir / '.secrets'
        _secrets_path.touch(exist_ok=True)
        _secrets_path.write_text(
            '\n'.join(
                [
                    _secret.split('=', 1)[0]
                    for _secret in list_response.secrets
                    if _secret.split('=', 1)[0] not in DEFAULT_SECRETS
                ],
            ),
        )

    if output == OutputFormat.json:
        rprint(json.dumps(list_response.model_dump(), indent=4))
        return

    if not list_response.secrets:
        rprint('No secrets found.')
        return

    data_table = Table()
    data_table.add_column('Secret Name', justify='center')

    if values:
        data_table.add_column('Secret Value', justify='center')

    for secret in list_response.secrets:
        if values:
            secret_name, secret_value = secret.split('=', 1)
            data_table.add_row(secret_name, secret_value)
        else:
            data_table.add_row(secret)

    rprint(data_table)


@secret_sub_app.callback(invoke_without_command=True)
def secret_list_callback(
    ctx: typer.Context,
    output: Annotated[OutputFormat, typer.Option('--output', '-o')] = OutputFormat.default,
    env_name: typing.Annotated[
        typing.Optional[str],  # noqa: UP007
        Option('--env', help='Environment name. Default is the current environment from configuration.'),
    ] = None,
    *,
    values: Annotated[bool, typer.Option('--values', '-v', help='Show secret values')] = False,
    sync: bool = Option(
        False,
        '--sync',
        help='Sync the dependencies from the Cloud Server to ".secrets".',
    ),
) -> None:
    """
    Lists the app secrets on the Cloud Server.
    """

    if ctx.invoked_subcommand is not None:
        return

    secret_list_command(
        ctx=ctx,
        output=output,
        values=values,
        env_name=env_name,
        sync=sync,
    )
