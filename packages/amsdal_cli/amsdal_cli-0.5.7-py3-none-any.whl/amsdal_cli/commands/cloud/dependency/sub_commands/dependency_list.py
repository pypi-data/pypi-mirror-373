import json
import tempfile
import typing
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.table import Table
from typer import Option

from amsdal_cli.commands.cloud.dependency.app import dependency_sub_app
from amsdal_cli.commands.cloud.enums import OutputFormat


def dependency_list_command(
    ctx: typer.Context,
    output: Annotated[OutputFormat, typer.Option('--output', '-o')] = OutputFormat.default,
    *,
    all_deps: bool = Option(False, '--all', '-a', help='List all dependencies.'),
    env_name: typing.Annotated[
        typing.Optional[str],  # noqa: UP007
        Option('--env', help='Environment name. Default is the current environment from configuration.'),
    ] = None,
    sync: bool = Option(
        False,
        '--sync',
        help='Sync the dependencies from the Cloud Server to ".dependencies".',
    ),
) -> None:
    """
    Shows a list of the app's dependencies on the Cloud Server.

    Example of usage:

    1. List of installed dependencies:
    ```bash
    amsdal cloud deps
    ```

    2. List of all supported dependencies:
    ```bash
    amsdal cloud deps --all
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
        rprint(rich_info(f'Listing dependencies for environment: {rich_highlight(env_name)}'))

    with tempfile.TemporaryDirectory() as _temp_dir:
        output_path: Path = Path(_temp_dir)
        app_builder = AppBuilder(
            cli_config=cli_config,
            config_path=cli_config.config_path,
        )
        app_builder.build(output_path, is_silent=True)
        manager: AsyncAmsdalManager | AmsdalManager

        manager = (
            AsyncAmsdalManager(raise_on_new_signup=True)
            if AmsdalConfigManager().get_config().async_mode
            else AmsdalManager(raise_on_new_signup=True)
        )

        manager.authenticate()

    AmsdalConfigManager().load_config(cli_config.config_path)

    try:
        list_response = manager.cloud_actions_manager.list_dependencies(
            env_name=env_name,
            application_uuid=cli_config.application_uuid,
            application_name=cli_config.application_name,
        )
    except AmsdalCloudError as e:
        rprint(rich_error(str(e)))
        raise typer.Exit(1) from e

    if sync:
        config_dir: Path = cli_config.app_directory / '.amsdal'
        config_dir.mkdir(exist_ok=True, parents=True)
        _deps_path: Path = config_dir / '.dependencies'
        _deps_path.touch(exist_ok=True)
        _deps_path.write_text('\n'.join(list_response.dependencies))

    if not list_response:
        return

    if output == OutputFormat.json:
        rprint(json.dumps(list_response.model_dump(), indent=4))
        return

    data_table = Table()

    if all_deps:
        data_table.add_column('Dependency Name', justify='left')
        data_table.add_column('Status', justify='left')

        for dependency in list_response.all:
            is_installed = dependency in list_response.dependencies
            data_table.add_row(
                rich_success(dependency) if is_installed else f'[i]{dependency}[/i]',
                rich_success('Installed') if is_installed else '[i]Not Installed[/i]',
            )

    else:
        if not list_response.dependencies:
            rprint('No dependencies found.')
            return

        data_table.add_column('Dependency Name', justify='center')

        for dependency in list_response.dependencies:
            data_table.add_row(dependency)

    rprint(data_table)


@dependency_sub_app.callback(invoke_without_command=True)
def dependency_list_callback(
    ctx: typer.Context,
    output: Annotated[OutputFormat, typer.Option('--output', '-o')] = OutputFormat.default,
    *,
    all_deps: bool = Option(False, '--all', '-a', help='List all dependencies.'),
    sync: bool = Option(
        False,
        '--sync',
        help='Sync the dependencies from the Cloud Server to ".dependencies".',
    ),
) -> None:
    """
    Lists the app dependencies on the Cloud Server.

    Args:
        ctx (typer.Context): The Typer context object.
        output (Annotated[OutputFormat, typer.Option]): The output format for the list.
        all_deps (bool): If True, list all dependencies.
        sync (bool): If True, sync the dependencies from the Cloud Server to ".dependencies".

    Returns:
        None
    """

    if ctx.invoked_subcommand is not None:
        return

    dependency_list_command(
        ctx=ctx,
        output=output,
        all_deps=all_deps,
        sync=sync,
    )
