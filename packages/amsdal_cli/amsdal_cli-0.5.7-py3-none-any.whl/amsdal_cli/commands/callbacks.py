import json
import os
from json import JSONDecodeError
from pathlib import Path

import typer
from amsdal_utils.config.manager import AmsdalConfigManager
from rich import print as rprint
from typer import Option

COMMANDS_DO_NOT_REQUIRE_APP_PATH = ('new', 'n', 'plugin', 'api-check')


def init_app_context(
    ctx: typer.Context,
    *,
    version: bool = Option(
        False,
        '--version',
        '-v',
        help='Check and show versions of amsdal packages',
    ),
) -> None:
    """
    AMSDAL CLI - a tool that provides the ability to create a new app,
    generate models, transactions, build, serve, and other useful features
    for the efficient building of new apps using AMSDAL Framework.

    Args:
        ctx (typer.Context): The Typer context object.
        version (bool, optional): If True, check and show versions of AMSDAL packages. Defaults to False.

    Returns:
        None
    """
    from amsdal_cli.commands.cloud.environments.utils import get_current_env
    from amsdal_cli.config.main import settings
    from amsdal_cli.utils.check_versions import check_latest_amsdal_version
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.text import CustomConfirm
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_highlight
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.vcs import get_vcs_service

    if version:
        check_latest_amsdal_version()
        return
    elif settings.CHECK_AMSDAL_VERSIONS:
        check_latest_amsdal_version()

    if not ctx.invoked_subcommand:
        return

    alias_commands_map = {
        'g': 'generate',
        'gen': 'generate',
        'n': 'new',
        'ci-cd': 'ci_cd',
        'reg-conn': 'register_connection',
    }
    _cmd = alias_commands_map.get(ctx.invoked_subcommand, ctx.invoked_subcommand)
    templates_path = Path(__file__).parent / _cmd / 'templates'

    if ctx.invoked_subcommand in COMMANDS_DO_NOT_REQUIRE_APP_PATH:
        ctx.meta['config'] = CliConfig(
            templates_path=templates_path,
            application_uuid=settings.AMSDAL_APPLICATION_UUID,
        )

        return

    app_path = Path(os.getcwd())
    cli_config = app_path / '.amsdal-cli'

    if not cli_config.exists():
        rprint(rich_error(f'The directory "{app_path.resolve()}" does not contain AMSDAL application.'))
        rprint('Use the "amsdal new --help" command to see details about how to create an application.')
        raise typer.Exit(1)

    with cli_config.open('rt') as config_file:
        try:
            ctx.meta['config'] = CliConfig(
                app_directory=app_path,
                templates_path=templates_path,
                **json.loads(config_file.read()),
            )
        except JSONDecodeError as err:
            rprint(rich_error(f'The config file "{cli_config.resolve()}" is corrupted.'))
            raise typer.Exit(1) from err

    config = ctx.meta['config']

    try:
        amsdal_config = AmsdalConfigManager().get_config()
    except Exception:
        AmsdalConfigManager().load_config(config.config_path)

    amsdal_config = AmsdalConfigManager().get_config()

    if not amsdal_config.config_dir:
        config_dir: Path = config.app_directory / '.amsdal'
        config_dir.mkdir(exist_ok=True, parents=True)
        amsdal_config.config_dir = config_dir

    if settings.AMSDAL_APPLICATION_UUID:
        config.application_uuid = settings.AMSDAL_APPLICATION_UUID

    vcs_service = get_vcs_service(config)
    ctx.meta['vcs_service'] = vcs_service

    current_branch = vcs_service.get_current_branch()
    current_env = get_current_env(config)
    if current_branch != current_env:
        if CustomConfirm.ask(
            rich_info(
                f'The current branch {rich_highlight(current_branch)} is different from the current '
                f'environment {rich_highlight(current_env)}. '
                'Would you like to checkout the current branch?'
            ),
            default=False,
            show_default=False,
            choices=['y', 'N'],
        ):
            vcs_service.checkout(current_env)
