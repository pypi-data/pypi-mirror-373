import asyncio
import random
from pathlib import Path
from typing import Annotated

import typer
from amsdal_utils.config.manager import AmsdalConfigManager
from rich import print as rprint

from amsdal_cli.commands.generate.app import sub_app
from amsdal_cli.commands.generate.enums import TestDataType
from amsdal_cli.commands.generate.enums import TestType


@sub_app.command(name='tests')
def generate_tests(
    ctx: typer.Context,
    model_name: str = typer.Option(..., help='The model name. It should be provided in PascalCase.'),
    test_type: TestType = typer.Option(TestType.UNIT.value, help='The type of test to generate.'),  # noqa: B008
    test_data_type: TestDataType = typer.Option(  # noqa: B008
        TestDataType.DYNAMIC.value,
        help='The type of test data to generate.',
    ),
    config: Annotated[Path, typer.Option(..., '--config', '-c')] = None,  # type: ignore # noqa: RUF013
    seed: int = typer.Option(0, help='The seed for the random number generator.'),
) -> None:
    """
    Generates tests for the given model.

    Examples of usage:

    1. Generate unit tests for the model `User`:
    ```bash
    amsdal generate tests --model-name User
    ```

    2. Generate unit tests for the model `User` with random test data:
    ```bash
    amsdal generate tests --model-name User --test-data-type=random
    ```

    3. Generate unit tests for the model `User` with dummy test data:
    ```bash
    amsdal generate tests --model-name User --test-data-type=dummy
    ```
    """
    asyncio.run(
        _generate_tests(
            ctx=ctx,
            model_name=model_name,
            test_type=test_type,
            test_data_type=test_data_type,
            config=config,
            seed=seed,
        )
    )


async def _generate_tests(
    ctx: typer.Context,
    model_name: str,
    test_type: TestType,
    test_data_type: TestDataType,
    config: Path,
    seed: int,
) -> None:
    import faker
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager

    from amsdal_cli.commands.generate.utils.tests.conftest_utils import create_conftest_if_not_exist
    from amsdal_cli.commands.generate.utils.tests.unit import generate_and_save_unit_tests
    from amsdal_cli.commands.serve.utils import async_build_app_and_check_migrations
    from amsdal_cli.commands.serve.utils import build_app_and_check_migrations
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_highlight
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_success

    random.seed(seed)
    faker.Faker.seed(seed)

    cli_config: CliConfig = ctx.meta['config']
    config_path = config or cli_config.config_path
    config_manager = AmsdalConfigManager()
    config_manager.load_config(config_path)

    create_conftest_if_not_exist(cli_config)
    app_source_path = cli_config.app_directory / cli_config.src_dir

    manager: AmsdalManager | AsyncAmsdalManager
    if config_manager.get_config().async_mode:
        manager = AsyncAmsdalManager()
        manager.pre_setup()
        await async_build_app_and_check_migrations(
            cli_config=cli_config,
            output_path=cli_config.app_directory,
            app_source_path=app_source_path,
            config_path=config_path,
            apply_fixtures=False,
            confirm_migrations=None,
            skip_migrations_check=True,
        )
    else:
        manager = AmsdalManager()
        manager.pre_setup()
        build_app_and_check_migrations(
            cli_config=cli_config,
            output_path=cli_config.app_directory,
            app_source_path=app_source_path,
            config_path=config_path,
            apply_fixtures=False,
            confirm_migrations=None,
            skip_migrations_check=True,
        )

    if test_type == TestType.UNIT:
        try:
            rprint(rich_info(f'Generating unit tests for {rich_highlight(model_name)}...'))

            if generate_and_save_unit_tests(model_name, cli_config, test_data_type=test_data_type):
                rprint(rich_success(f'Unit tests for {rich_highlight(model_name)} generated successfully.'))
        except Exception as e:
            rprint(rich_error(str(e)))
            raise typer.Exit(1) from e
        finally:
            if config_manager.get_config().async_mode:
                await manager.teardown()  # type: ignore[misc]
            else:
                manager.teardown()
