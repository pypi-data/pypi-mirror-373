from pathlib import Path
from typing import TYPE_CHECKING

from rich import print as rprint

from amsdal_cli.commands.build.services.mixin import BuildMixin

if TYPE_CHECKING:
    from amsdal_cli.utils.cli_config import CliConfig


class AppBuilder(BuildMixin):
    def __init__(self, cli_config: 'CliConfig', config_path: Path) -> None:
        from amsdal_models.classes.class_manager import ClassManager

        self.cli_config = cli_config
        self.source_path = cli_config.app_directory / cli_config.src_dir
        self.config_path = config_path
        self.class_manager = ClassManager()

    def build(self, output: Path, *, is_silent: bool = False) -> None:
        from amsdal_cli.utils.cli_config import ModelsFormat
        from amsdal_cli.utils.text import rich_info
        from amsdal_cli.utils.text import rich_success
        from amsdal_cli.utils.text import rich_warning

        self.pre_build(output)

        if not is_silent:
            rprint(rich_info('Building transactions...'), end=' ')
        self.build_transactions(self.source_path)
        if not is_silent:
            rprint(rich_success('OK!'))

        if not is_silent:
            rprint(rich_info('Building models...'), end=' ')
        if self.cli_config.models_format == ModelsFormat.JSON:
            self.build_models(self.cli_config)
        elif (self.source_path / 'models').exists():
            self.copy_class_models(self.source_path / 'models')
        if not is_silent:
            rprint(rich_success('OK!'))

        if output == Path('.'):
            if not is_silent:
                rprint(rich_warning('No output directory specified, skipping config.yml generation.'))
        else:
            # build config file
            from amsdal_cli.commands.build.utils.build_config_file import build_config_file

            build_config_file(
                output_path=output,
                config_path=self.config_path,
                no_input=True,
                is_silent=is_silent,
            )

        if not is_silent:
            rprint(rich_info('Building static files...'), end=' ')
        self.build_static_files(self.source_path)
        if not is_silent:
            rprint(rich_success('OK!'))

        if not is_silent:
            rprint(rich_info('Building fixtures...'), end=' ')
        self.build_fixtures(self.source_path)
        if not is_silent:
            rprint(rich_success('OK!'))

        if not is_silent:
            rprint(rich_info('Building migrations...'), end=' ')
        self.build_migrations(self.source_path)
        if not is_silent:
            rprint(rich_success('OK!'))

    def pre_build(self, output: Path) -> None:
        from amsdal.configs.main import settings
        from amsdal_utils.config.manager import AmsdalConfigManager

        settings.override(
            APP_PATH=output,
            USER_MODELS_MODULE_PATH=output / 'models',
        )

        settings.user_models_path.mkdir(parents=True, exist_ok=True)
        (settings.user_models_path / '__init__.py').touch(exist_ok=True)

        config_manager = AmsdalConfigManager()
        config_manager.load_config(self.config_path)
