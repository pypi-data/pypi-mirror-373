import asyncio
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen

import typer
from amsdal.manager import AmsdalManager
from amsdal.manager import AsyncAmsdalManager
from amsdal.utils.tests.enums import DbExecutionType
from amsdal.utils.tests.enums import LakehouseOption
from amsdal.utils.tests.enums import StateOption

from amsdal_cli.app import app
from amsdal_cli.commands.serve.utils import async_build_app_and_check_migrations
from amsdal_cli.commands.serve.utils import build_app_and_check_migrations
from amsdal_cli.utils.cli_config import CliConfig

PYTEST_COMMAND = 'pytest'


def _init(cli_config: CliConfig, app_source_path: Path, config_path: Path) -> None:
    manager = AmsdalManager()
    if not manager.is_setup:
        manager.setup()
    build_app_and_check_migrations(
        cli_config=cli_config,
        output_path=cli_config.app_directory,
        app_source_path=app_source_path,
        config_path=config_path,
        apply_fixtures=False,
        confirm_migrations=None,
    )
    manager.authenticate()
    manager.teardown()

    AmsdalManager.invalidate()


async def _async_init(cli_config: CliConfig, app_source_path: Path, config_path: Path) -> None:
    amsdal_manager = AsyncAmsdalManager()
    if not amsdal_manager.is_setup:
        await amsdal_manager.setup()
    await async_build_app_and_check_migrations(
        cli_config=cli_config,
        output_path=cli_config.app_directory,
        app_source_path=app_source_path,
        config_path=config_path,
        apply_fixtures=False,
        confirm_migrations=None,
    )
    amsdal_manager.authenticate()
    await amsdal_manager.teardown()

    AsyncAmsdalManager.invalidate()


@app.command(
    name='tests, test',
    context_settings={
        'allow_extra_args': True,
        'ignore_unknown_options': True,
    },
)
def run_tests(
    ctx: typer.Context,
    db_execution_type: DbExecutionType = DbExecutionType.include_state_db,
    state_option: StateOption = StateOption.sqlite,
    lakehouse_option: LakehouseOption = LakehouseOption.sqlite,
) -> None:
    """
    Runs tests with the specified database execution type, state option, and lakehouse option.

    Example usage:

    1. Run tests on SQLite database:
    ```bash
    amsdal tests
    ```

    2. Run tests on PostgreSQL database:
    ```bash
    amsdal tests --state-option postgres --lakehouse-option postgres
    ```

    3. Run tests with lakehouse-only execution type:
    ```bash
    amsdal tests --db-execution-type lakehouse_only
    ```
    """

    from amsdal_utils.config.manager import AmsdalConfigManager

    from amsdal_cli.utils.cli_config import CliConfig

    cli_config: CliConfig = ctx.meta['config']
    config_manager = AmsdalConfigManager()
    config_manager.load_config(cli_config.config_path)
    config_path = cli_config.config_path
    app_source_path = cli_config.app_directory / cli_config.src_dir

    if AmsdalConfigManager().get_config().async_mode:
        asyncio.run(_async_init(cli_config=cli_config, app_source_path=app_source_path, config_path=config_path))
    else:
        _init(cli_config=cli_config, app_source_path=app_source_path, config_path=config_path)

    AmsdalConfigManager.invalidate()

    with Popen(  # noqa: S603
        [
            PYTEST_COMMAND,
            cli_config.src_dir,
            '--color=yes',
            '--db_execution_type',
            db_execution_type,
            '--state_option',
            state_option,
            '--lakehouse_option',
            lakehouse_option,
            *ctx.args,
        ],
        stdout=PIPE,
        bufsize=1,
        universal_newlines=True,
    ) as p:
        if p.stdout is not None:
            for line in p.stdout:
                print(line, end='')  # noqa: T201
