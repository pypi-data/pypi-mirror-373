import ast
import importlib
import json
import pkgutil
import sys
from pathlib import Path

from amsdal_models.schemas.object_schema import model_to_object_schema
from amsdal_utils.config.manager import AmsdalConfigManager
from amsdal_utils.schemas.schema import ObjectSchema
from amsdal_utils.utils.text import classify
from amsdal_utils.utils.text import to_snake_case

from amsdal_cli.commands.generate.enums import MODEL_JSON_FILE
from amsdal_cli.commands.generate.enums import TestDataType
from amsdal_cli.commands.generate.utils.tests.async_mode_utils import maybe_await
from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.cli_config import ModelsFormat
from amsdal_cli.utils.text import rich_highlight


def find_model_class(package: str, class_name: str) -> type:
    importlib.invalidate_caches()

    prefix = package + '.'
    for mod_name in list(sys.modules):
        if mod_name == package or mod_name.startswith(prefix):
            del sys.modules[mod_name]

    spec = importlib.util.find_spec(package)
    if not spec or not spec.submodule_search_locations:
        msg = f"Can't find package {package!r} on disk"
        raise ImportError(msg)

    paths = spec.submodule_search_locations

    for _, full_name, _ in pkgutil.walk_packages(paths, prefix=prefix):
        module = importlib.import_module(full_name)

        if hasattr(module, class_name):
            return getattr(module, class_name)

    msg = f'Could not find class {class_name!r} in package {package!r}'
    raise ImportError(msg)


def get_class_schema(models_dir: Path, class_name: str, cli_config: CliConfig) -> ObjectSchema:
    model_name = classify(class_name)
    name = to_snake_case(model_name)

    if cli_config.models_format == ModelsFormat.PY:
        # model_class = import_class(f'models.{name}.{class_name}')
        model_class = find_model_class('models', class_name)

        return model_to_object_schema(model_class)
    else:
        model_json_path = models_dir / name / MODEL_JSON_FILE

        if not model_json_path.exists():
            msg = f'Model JSON file not found for {rich_highlight(model_name)}.'
            raise ValueError(msg)

        model_dict = json.loads(model_json_path.read_text())

        return ObjectSchema(**model_dict)


def object_creation_call(
    model_name_snake_case: str,
    object_schema: ObjectSchema,
    models_dir: Path,
    imports_set: set[tuple[str, str]],
    test_data_type: TestDataType,
    cli_config: CliConfig,
) -> ast.Call | ast.Await:
    if AmsdalConfigManager().get_config().async_mode:
        save_name = 'asave'
    else:
        save_name = 'save'

    return maybe_await(
        ast.Call(
            func=ast.Attribute(
                value=object_init_call(
                    model_name_snake_case,
                    object_schema,
                    models_dir,
                    imports_set,
                    test_data_type,
                    cli_config=cli_config,
                ),
                attr=save_name,
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        )
    )


def object_init_call(
    model_name_snake_case: str,
    object_schema: ObjectSchema,
    models_dir: Path,
    imports_set: set[tuple[str, str]],
    test_data_type: TestDataType,
    cli_config: CliConfig,
) -> ast.Call:
    from amsdal_cli.commands.generate.utils.tests.type_utils import keywords_for_schema

    if cli_config.models_format == ModelsFormat.PY:
        model_class = find_model_class('models', object_schema.title)
        imports_set.add((model_class.__module__, object_schema.title))
    else:
        imports_set.add((f'models.{model_name_snake_case}', object_schema.title))

    return ast.Call(
        func=ast.Name(id=object_schema.title, ctx=ast.Load()),
        args=[],
        keywords=keywords_for_schema(
            object_schema,
            models_dir,
            imports_set,
            test_data_type=test_data_type,
            cli_config=cli_config,
        ),
    )
