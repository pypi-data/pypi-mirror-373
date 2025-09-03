from pathlib import Path

from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.cli_config import ModelsFormat


def build_models(
    cli_config: CliConfig,
    config_path: Path,
    build_dir: Path,
) -> None:
    from amsdal_cli.commands.build.services.builder import AppBuilder

    source_path = cli_config.app_directory / cli_config.src_dir
    app_builder = AppBuilder(
        cli_config=cli_config,
        config_path=config_path,
    )

    app_builder.pre_build(build_dir)

    if cli_config.models_format == ModelsFormat.JSON:
        app_builder.build_models(cli_config)
    elif (source_path / 'models').exists():
        app_builder.copy_class_models(source_path / 'models')
