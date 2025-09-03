import importlib
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amsdal_cli.utils.cli_config import CliConfig


class BuildMixin:
    """
    Provides methods to build models, transactions, static files, migrations, and fixtures for a CLI application.
    """

    @classmethod
    def build_models(cls, cli_config: 'CliConfig') -> None:
        """
        Builds models from the specified user schemas path and predefined schema directories.

        Args:
            cli_config (CliConfig): CLI config object.

        Returns:
            None
        """

        from amsdal.configs.main import settings
        from amsdal_models.builder.services.class_builder import ClassBuilder
        from amsdal_utils.models.enums import ModuleType

        from amsdal_cli.utils.schema_repository import build_schema_repository

        schema_repository = build_schema_repository(cli_config)
        class_builder = ClassBuilder()

        for user_schema in schema_repository.user_schemas:
            class_builder.build(
                models_package_path=settings.user_models_path,
                models_module_path=settings.USER_MODELS_MODULE,
                object_schema=user_schema,
                module_type=ModuleType.USER,
                dependencies=schema_repository.model_module_info,  # type: ignore[arg-type]
                indent_width=' ' * cli_config.indent,
            )

    @staticmethod
    def copy_class_models(models_source_path: Path) -> None:
        from amsdal.configs.main import settings

        shutil.copytree(  # type: ignore[type-var]
            models_source_path,
            settings.USER_MODELS_MODULE_PATH,
            dirs_exist_ok=True,
        )

    @staticmethod
    def build_transactions(cli_app_path: Path) -> None:
        """
        Builds transactions from the specified CLI application path.

        Args:
            cli_app_path (Path): The path to the CLI application directory.

        Returns:
            None
        """

        from amsdal.configs.main import settings

        from amsdal_cli.commands.build.schemas.loaders.cli_transactions_loader import CliTransactionsLoader

        transactions_loader = CliTransactionsLoader(cli_app_path)
        transactions_path = settings.transactions_root_path

        # Remove old transactions directory
        shutil.rmtree(transactions_path, ignore_errors=True)

        transactions_path.mkdir(exist_ok=True)
        (transactions_path / '__init__.py').touch(exist_ok=True)

        for item in transactions_loader.iter_transactions():
            if item.is_dir():
                shutil.copytree(item, transactions_path / item.name, dirs_exist_ok=True)
            else:
                shutil.copy(item, transactions_path / item.name)

    @staticmethod
    def build_static_files(cli_app_path: Path) -> None:
        """
        Builds static files from the specified CLI application path.

        Args:
            cli_app_path (Path): The path to the CLI application directory.

        Returns:
            None
        """

        from amsdal.configs.main import settings

        from amsdal_cli.commands.build.schemas.loaders.cli_statics_loader import CliStaticsLoader

        statics_loader = CliStaticsLoader(cli_app_path)

        if not settings.static_root_path.exists():
            settings.static_root_path.mkdir(parents=True, exist_ok=True)

        item: Path
        for item in statics_loader.iter_static():
            static_file = settings.static_root_path / item.name
            static_file.write_bytes(item.read_bytes())

    @staticmethod
    def build_migrations(cli_app_path: Path) -> None:
        """
        Builds migrations from the specified CLI application path.

        Args:
            cli_app_path (Path): The path to the CLI application directory.

        Returns:
            None
        """

        from amsdal.configs.main import settings

        if not (cli_app_path / settings.MIGRATIONS_DIRECTORY_NAME).exists():
            return

        migrations_path = settings.APP_PATH / settings.MIGRATIONS_DIRECTORY_NAME

        # Remove old migrations directory
        shutil.rmtree(migrations_path, ignore_errors=True)

        migrations_path.mkdir(exist_ok=True)
        shutil.copytree(cli_app_path / settings.MIGRATIONS_DIRECTORY_NAME, migrations_path, dirs_exist_ok=True)

    @staticmethod
    def build_fixtures(cli_app_path: Path) -> None:
        """
        Builds fixtures from the specified CLI application path.

        Args:
            cli_app_path (Path): The path to the CLI application directory.

        Returns:
            None
        """

        from amsdal.configs.main import settings

        schemas_dirs = [cli_app_path]

        for contrib_path in settings.CONTRIBS:
            module_path, _ = contrib_path.rsplit('.', 1)
            models_path = (
                Path(
                    importlib.import_module(module_path).__file__,  # type: ignore[arg-type]
                ).parent
                / 'models'
            )
            schemas_dirs.append(models_path)

        target_fixtures_path = settings.APP_PATH / 'fixtures'

        shutil.rmtree(target_fixtures_path, ignore_errors=True)
        target_fixtures_path.mkdir(exist_ok=True)
        expected_fixtures_path = cli_app_path / 'fixtures'
        if expected_fixtures_path.exists() and expected_fixtures_path.is_dir():
            shutil.copytree(expected_fixtures_path, target_fixtures_path, dirs_exist_ok=True)

    @staticmethod
    def _reimport_models() -> None:
        from amsdal_models.classes.class_manager import ClassManager

        class_manager = ClassManager()
        class_manager.teardown()
