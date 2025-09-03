import importlib
from typing import TYPE_CHECKING

from amsdal.schemas.interfaces import BaseSchemaLoader
from amsdal.schemas.interfaces import ModulePathType
from amsdal_utils.schemas.schema import ObjectSchema

if TYPE_CHECKING:
    from amsdal.schemas.repository import SchemaRepository

    from amsdal_cli.utils.cli_config import CliConfig


class DummySchemaLoader(BaseSchemaLoader):
    @property
    def schemas_per_module(self) -> dict[ModulePathType, list[ObjectSchema]]:
        return {}

    def load(self) -> list[ObjectSchema]:
        return []

    def load_sorted(self) -> tuple[list[ObjectSchema], list[ObjectSchema]]:
        return [], []


def build_schema_repository(
    cli_config: 'CliConfig',
    *,
    skip_user_models: bool = False,
) -> 'SchemaRepository':
    from amsdal.configs.main import settings
    from amsdal.schemas.repository import SchemaRepository
    from amsdal_models.schemas.class_schema_loader import ClassMultiDirectoryJsonLoader
    from amsdal_models.schemas.class_schema_loader import ClassSchemaLoader
    from amsdal_utils.models.enums import ModuleType

    from amsdal_cli.commands.build.schemas.data_models.schemas_directory import SchemasDirectory
    from amsdal_cli.commands.build.schemas.schema_json_loader import SchemaJsonLoader
    from amsdal_cli.utils.cli_config import ModelsFormat

    _contrib_modules_paths: list[str] = []

    for contrib_path in settings.CONTRIBS:
        contrib_module_path, _, _ = contrib_path.rsplit('.', 2)
        contrib_models_module_path = f'{contrib_module_path}.{settings.CONTRIB_MODELS_PACKAGE_NAME}'

        try:
            _module = importlib.import_module(contrib_models_module_path)
        except ImportError:
            continue

        _contrib_modules_paths.append(contrib_models_module_path)

    target_module_type = ModuleType.CONTRIB if cli_config.is_plugin else ModuleType.USER

    if cli_config.models_format == ModelsFormat.PY:
        if skip_user_models:
            user_schema_loader = DummySchemaLoader()
        else:
            user_schema_loader = ClassSchemaLoader(
                settings.USER_MODELS_MODULE,
                class_filter=lambda cls: cls.__module_type__ == target_module_type,
            )  # type: ignore[assignment]
    else:
        _models_path = cli_config.app_directory / cli_config.src_dir / 'models'
        user_schema_loader = SchemaJsonLoader(  # type: ignore[assignment]
            SchemasDirectory(
                path=_models_path,
                module_path=settings.USER_MODELS_MODULE,
                module_type=target_module_type,
            ),
        )

    return SchemaRepository(
        type_schema_loader=ClassSchemaLoader(settings.TYPE_MODELS_MODULE),
        core_schema_loader=ClassSchemaLoader(settings.CORE_MODELS_MODULE),
        contrib_schema_loader=ClassMultiDirectoryJsonLoader(_contrib_modules_paths),
        user_schema_loader=user_schema_loader,  # type: ignore[arg-type]
    )
