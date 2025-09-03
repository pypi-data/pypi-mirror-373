import asyncio
import sys
import tempfile
import typing
from pathlib import Path

import typer
from amsdal.cloud.enums import DeployType
from amsdal.cloud.enums import LakehouseOption
from rich import print as rprint
from typer import Option

from amsdal_cli.commands.cloud.deploy.app import deploy_sub_app

if typing.TYPE_CHECKING:
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager

    from amsdal_cli.utils.cli_config import CliConfig


@deploy_sub_app.command('new, n')
def deploy_command(
    ctx: typer.Context,
    deploy_type: DeployType = DeployType.include_state_db,
    lakehouse_type: LakehouseOption = LakehouseOption.postgres,
    env_name: typing.Annotated[
        typing.Optional[str],  # noqa: UP007
        Option('--env', help='Environment name. Default is the current environment from configuration.'),
    ] = None,
    from_env: typing.Optional[str] = Option(None, '--from-env', help='Environment name to copy from.'),  # noqa: UP007
    *,
    no_input: bool = Option(False, '--no-input', help='Do not prompt for input.'),
    skip_checks: bool = Option(
        False,
        '--skip-checks',
        help='Skip checking secrets and dependencies before deploying.',
    ),
) -> None:
    """
    Deploys the app to the Cloud Server.
    """
    asyncio.run(
        _deploy(
            ctx=ctx,
            deploy_type=deploy_type,
            lakehouse_type=lakehouse_type,
            env_name=env_name,
            from_env=from_env,
            no_input=no_input,
            skip_checks=skip_checks,
        )
    )


async def _deploy(
    ctx: typer.Context,
    deploy_type: DeployType,
    lakehouse_type: LakehouseOption,
    env_name: str | None,
    from_env: str | None,
    *,
    no_input: bool,
    skip_checks: bool,
) -> None:
    from amsdal.errors import AmsdalCloudError
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_utils.config.manager import AmsdalConfigManager

    from amsdal_cli.commands.build.services.builder import AppBuilder
    from amsdal_cli.commands.cloud.environments.utils import get_current_env
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.text import CustomConfirm
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_highlight
    from amsdal_cli.utils.text import rich_info
    from amsdal_cli.utils.text import rich_warning

    cli_config: CliConfig = ctx.meta['config']
    app_source_path = cli_config.app_directory / cli_config.src_dir
    env_name = env_name or get_current_env(cli_config)

    if cli_config.verbose:
        rprint(rich_info(f'Deploying to environment: {rich_highlight(env_name)}'))

    with tempfile.TemporaryDirectory() as _temp_dir:
        output_path: Path = Path(_temp_dir)
        app_builder = AppBuilder(
            cli_config=cli_config,
            config_path=cli_config.config_path,
        )
        app_builder.build(output_path, is_silent=True)

        manager: AsyncAmsdalManager | AmsdalManager | None = None
        try:
            if AmsdalConfigManager().get_config().async_mode:
                manager = AsyncAmsdalManager()
                await _async_check_missing_generated_migrations(cli_config, manager, app_source_path)
            else:
                manager = AmsdalManager()
                _check_missing_generated_migrations(cli_config, manager, app_source_path)

            manager.authenticate()

            if not skip_checks:
                try:
                    list_response_deps = manager.cloud_actions_manager.list_dependencies(
                        env_name=env_name,
                        application_uuid=cli_config.application_uuid,
                        application_name=cli_config.application_name,
                    )
                except AmsdalCloudError as e:
                    rprint(rich_error(f'Failed to loading dependencies: {e}'))
                    raise typer.Exit(1) from e

                config_dir: Path = cli_config.app_directory / '.amsdal'
                config_dir.mkdir(exist_ok=True, parents=True)
                _deps_path: Path = config_dir / '.dependencies'
                _deps_path.touch(exist_ok=True)
                _deps = set(_deps_path.read_text().split('\n'))
                _diff_deps = sorted(filter(None, _deps - set(list_response_deps.dependencies)))

                if _diff_deps:
                    rprint(
                        rich_warning(
                            f'The following dependencies are missing: {", ".join(map(rich_highlight, _diff_deps))}'
                        )
                    )

                    if no_input:
                        rprint(rich_info('Installing missing dependencies...'))
                        install_deps = True
                    else:
                        install_deps = CustomConfirm.ask(
                            rich_info('Do you want to install the missing dependencies?'),
                            default=False,
                            show_default=False,
                            choices=['y', 'N'],
                        )

                    if not install_deps:
                        rprint(
                            rich_info('Use "amsdal cloud dependencies new NAME" to install the missing dependencies.')
                        )
                        raise typer.Exit(1)

                    for dependency_name in _diff_deps:
                        try:
                            manager.cloud_actions_manager.add_dependency(
                                dependency_name=dependency_name,
                                env_name=env_name,
                                application_uuid=cli_config.application_uuid,
                                application_name=cli_config.application_name,
                            )
                        except AmsdalCloudError as e:
                            rprint(rich_error(str(e)))
                            raise typer.Exit(1) from e

                try:
                    list_response_secrets = manager.cloud_actions_manager.list_secrets(
                        with_values=False,
                        env_name=env_name,
                        application_uuid=cli_config.application_uuid,
                        application_name=cli_config.application_name,
                    )
                except AmsdalCloudError as e:
                    rprint(rich_error(f'Failed to loading secrets: {e}'))
                    raise typer.Exit(1) from e

                _secrets_path: Path = config_dir / '.secrets'
                _secrets_path.touch(exist_ok=True)
                _secrets = set(_secrets_path.read_text().split('\n'))
                _diff_secrets = sorted(filter(None, _secrets - set(list_response_secrets.secrets)))

                if _diff_secrets:
                    rprint(rich_error(f'The following secrets are missing: {", ".join(_diff_secrets)}'))
                    raise typer.Exit(1)

            try:
                manager.cloud_actions_manager.create_deploy(
                    deploy_type=deploy_type.value,
                    lakehouse_type=lakehouse_type.value,
                    env_name=env_name,
                    from_env=from_env,
                    application_uuid=cli_config.application_uuid,
                    application_name=cli_config.application_name,
                    no_input=no_input,
                )
            except AmsdalCloudError as e:
                if str(e) in ['Same environment name', 'same_environment_name']:
                    rprint(
                        rich_error(
                            f'Trying to deploy {rich_highlight(env_name)} environment from '
                            f'{rich_highlight(str(from_env))}. Please check the environment names.'
                        )
                    )
                elif str(e) in ['Environment not found', 'environment_not_found']:
                    rprint(
                        rich_error(
                            f'Environment {rich_highlight(from_env if from_env else env_name)} not found. '
                            'Please check the environment name.'
                        )
                    )

                elif str(e) in ['Environment not deployed', 'environment_not_deployed']:
                    rprint(
                        rich_error(
                            f'Environment {rich_highlight(str(from_env))} is not deployed. '
                            'Please check the environment name.'
                        )
                    )

                else:
                    rprint(rich_error(str(e)))

                raise typer.Exit(1) from e
        finally:
            if manager:
                if AmsdalConfigManager().get_config().async_mode:
                    if manager.is_setup:
                        await manager.teardown()  # type: ignore[misc]
                    else:
                        AsyncAmsdalManager.invalidate()
                elif manager.is_setup:
                    manager.teardown()
                else:
                    AmsdalManager.invalidate()


def _check_missing_generated_migrations(
    cli_config: 'CliConfig',
    amsdal_manager: 'AmsdalManager',
    app_source_path: Path,
) -> None:
    """
    Check if there are missing migrations.

    Args:
        amsdal_manager (AmsdalManager): The Amsdal manager instance.

    Returns:
        None
    """
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal_models.migration.file_migration_generator import FileMigrationGenerator

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME
    from amsdal_cli.utils.cli_config import ModelsFormat
    from amsdal_cli.utils.schema_repository import build_schema_repository
    from amsdal_cli.utils.text import rich_error

    amsdal_manager.pre_setup()

    if not amsdal_manager.is_setup:
        amsdal_manager.setup()

    if not amsdal_manager.is_authenticated:
        amsdal_manager.authenticate()

    amsdal_manager.post_setup()  # type: ignore[call-arg]
    migrations_dir = app_source_path / MIGRATIONS_DIR_NAME
    cli_config.models_format = ModelsFormat.PY
    schema_repository = build_schema_repository(cli_config=cli_config)
    generator = FileMigrationGenerator(
        core_migrations_path=CORE_MIGRATIONS_PATH,
        app_migrations_path=migrations_dir,
        contrib_migrations_directory_name=settings.CONTRIB_MODELS_PACKAGE_NAME,
    )
    generator.init_state()

    operations = generator.app_file_migration_generator.generate_operations(schema_repository.user_schemas)

    if operations:
        rprint(rich_error('Missing generated migrations. Use `amsdal migrations new` to fix. Exiting...'))
        sys.exit(1)


async def _async_check_missing_generated_migrations(
    cli_config: 'CliConfig',
    amsdal_manager: 'AsyncAmsdalManager',
    app_source_path: Path,
) -> None:
    """
    Check if there are missing migrations.

    Args:
        amsdal_manager (AsyncAmsdalManager): The Amsdal manager instance.

    Returns:
        None
    """
    from amsdal.configs.constants import CORE_MIGRATIONS_PATH
    from amsdal.configs.main import settings
    from amsdal_models.migration.file_migration_generator import AsyncFileMigrationGenerator

    from amsdal_cli.commands.migrations.constants import MIGRATIONS_DIR_NAME
    from amsdal_cli.utils.cli_config import ModelsFormat
    from amsdal_cli.utils.schema_repository import build_schema_repository
    from amsdal_cli.utils.text import rich_error

    amsdal_manager.pre_setup()

    if not amsdal_manager.is_setup:
        await amsdal_manager.setup()

    if not amsdal_manager.is_authenticated:
        amsdal_manager.authenticate()

    await amsdal_manager.post_setup()  # type: ignore[call-arg, misc]

    migrations_dir = app_source_path / MIGRATIONS_DIR_NAME

    cli_config.models_format = ModelsFormat.PY
    schema_repository = build_schema_repository(cli_config=cli_config)
    generator = AsyncFileMigrationGenerator(
        core_migrations_path=CORE_MIGRATIONS_PATH,
        app_migrations_path=migrations_dir,
        contrib_migrations_directory_name=settings.CONTRIB_MODELS_PACKAGE_NAME,
    )
    await generator.init_state()

    operations = generator.app_file_migration_generator.generate_operations(schema_repository.user_schemas)

    if operations:
        rprint(rich_error('Missing generated migrations. Use `amsdal migrations new` to fix. Exiting...'))
        sys.exit(1)
