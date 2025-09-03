import ast
import sys
from pathlib import Path

import astor
import black
import isort
from amsdal_utils.config.manager import AmsdalConfigManager
from amsdal_utils.schemas.schema import ObjectSchema
from amsdal_utils.utils.text import classify
from amsdal_utils.utils.text import to_snake_case
from black.mode import TargetVersion

from amsdal_cli.commands.generate.enums import TestDataType
from amsdal_cli.commands.generate.utils.tests.async_mode_utils import maybe_await
from amsdal_cli.commands.generate.utils.tests.function_utils import test_function_arguments
from amsdal_cli.commands.generate.utils.tests.function_utils import test_function_decorator_list
from amsdal_cli.commands.generate.utils.tests.model_utils import get_class_schema
from amsdal_cli.commands.generate.utils.tests.model_utils import object_creation_call
from amsdal_cli.commands.generate.utils.tests.model_utils import object_init_call
from amsdal_cli.commands.generate.utils.tests.type_utils import generate_values_for_type_data
from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.text import CustomConfirm
from amsdal_cli.utils.text import rich_highlight
from amsdal_cli.utils.text import rich_info


def _function_def() -> type[ast.FunctionDef | ast.AsyncFunctionDef]:
    if AmsdalConfigManager().get_config().async_mode:
        return ast.AsyncFunctionDef

    return ast.FunctionDef


def _assert_state_count(number: int, model: str) -> ast.Assert:
    if AmsdalConfigManager().get_config().async_mode:
        execute_name = 'aexecute'
    else:
        execute_name = 'execute'

    return ast.Assert(
        test=ast.Compare(
            left=ast.Constant(value=number),
            ops=[ast.Eq()],
            comparators=[
                maybe_await(
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Attribute(
                                                value=ast.Name(id=model, ctx=ast.Load()),
                                                attr='objects',
                                                ctx=ast.Load(),
                                            ),
                                            attr='all',
                                            ctx=ast.Load(),
                                        ),
                                        args=[],
                                        keywords=[],
                                    ),
                                    attr='count',
                                    ctx=ast.Load(),
                                ),
                                args=[],
                                keywords=[],
                            ),
                            attr=execute_name,
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    )
                )
            ],
        )
    )


def _assert_lakehouse_count(number: int, model: str) -> ast.Assert:
    if AmsdalConfigManager().get_config().async_mode:
        execute_name = 'aexecute'
    else:
        execute_name = 'execute'

    return ast.Assert(
        test=ast.Compare(
            left=ast.Constant(value=number),
            ops=[ast.Eq()],
            comparators=[
                maybe_await(
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Call(
                                                func=ast.Attribute(
                                                    value=ast.Attribute(
                                                        value=ast.Name(id=model, ctx=ast.Load()),
                                                        attr='objects',
                                                        ctx=ast.Load(),
                                                    ),
                                                    attr='all',
                                                    ctx=ast.Load(),
                                                ),
                                                args=[],
                                                keywords=[],
                                            ),
                                            attr='using',
                                            ctx=ast.Load(),
                                        ),
                                        args=[ast.Name(id='LAKEHOUSE_DB_ALIAS', ctx=ast.Load())],
                                        keywords=[],
                                    ),
                                    attr='count',
                                    ctx=ast.Load(),
                                ),
                                args=[],
                                keywords=[],
                            ),
                            attr=execute_name,
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    )
                )
            ],
        )
    )


def _create_test(
    model_name_snake_case: str,
    object_schema: ObjectSchema,
    models_dir: Path,
    test_data_type: TestDataType,
    cli_config: CliConfig,
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    if AmsdalConfigManager().get_config().async_mode:
        save_name = 'asave'
        execute_name = 'aexecute'
    else:
        save_name = 'save'
        execute_name = 'execute'

    # create `obj` object from type description and save
    imports_set: set[tuple[str, str]] = set()
    object_init_expr = object_init_call(
        model_name_snake_case,
        object_schema,
        models_dir,
        imports_set,
        test_data_type,
        cli_config=cli_config,
    )

    if sys.version_info >= (3, 12):
        return _function_def()(
            name=f'test_create_{model_name_snake_case}',
            args=test_function_arguments(),
            body=[
                *[ast.ImportFrom(module=module, names=[ast.alias(name=name)], level=0) for module, name in imports_set],
                _assert_state_count(0, object_schema.title),
                _assert_lakehouse_count(0, object_schema.title),
                ast.Assign(
                    targets=[
                        ast.Name(id='obj', ctx=ast.Store()),
                    ],
                    value=object_init_expr,
                ),
                ast.Expr(
                    value=maybe_await(
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='obj', ctx=ast.Load()),
                                attr=save_name,
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        )
                    )
                ),
                _assert_state_count(1, object_schema.title),
                _assert_lakehouse_count(1, object_schema.title),
                ast.Assert(
                    test=ast.Compare(
                        left=ast.Constant(value=1),
                        ops=[ast.Eq()],
                        comparators=[
                            maybe_await(
                                ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Call(
                                            func=ast.Attribute(
                                                value=ast.Call(
                                                    func=ast.Attribute(
                                                        value=ast.Attribute(
                                                            value=ast.Name(
                                                                id=object_schema.title,
                                                                ctx=ast.Load(),
                                                            ),
                                                            attr='objects',
                                                            ctx=ast.Load(),
                                                        ),
                                                        attr='filter',
                                                        ctx=ast.Load(),
                                                    ),
                                                    args=[],
                                                    keywords=[
                                                        ast.keyword(
                                                            arg='_address__object_id',
                                                            value=ast.Attribute(
                                                                value=ast.Name(
                                                                    id='obj',
                                                                    ctx=ast.Load(),
                                                                ),
                                                                attr='object_id',
                                                                ctx=ast.Load(),
                                                            ),
                                                        )
                                                    ],
                                                ),
                                                attr='count',
                                                ctx=ast.Load(),
                                            ),
                                            args=[],
                                            keywords=[],
                                        ),
                                        attr=execute_name,
                                        ctx=ast.Load(),
                                    ),
                                    args=[],
                                    keywords=[],
                                )
                            )
                        ],
                    )
                ),
            ],
            decorator_list=test_function_decorator_list(),
            returns=ast.Constant(value=None),
            type_comment=None,
            type_params=[],
        )
    else:
        return _function_def()(
            name=f'test_create_{model_name_snake_case}',
            args=test_function_arguments(),
            body=[
                *[ast.ImportFrom(module=module, names=[ast.alias(name=name)], level=0) for module, name in imports_set],
                _assert_state_count(0, object_schema.title),
                _assert_lakehouse_count(0, object_schema.title),
                ast.Assign(
                    targets=[
                        ast.Name(id='obj', ctx=ast.Store()),
                    ],
                    value=object_init_expr,
                ),
                ast.Expr(
                    value=maybe_await(
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='obj', ctx=ast.Load()),
                                attr=save_name,
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        )
                    )
                ),
                _assert_state_count(1, object_schema.title),
                _assert_lakehouse_count(1, object_schema.title),
                ast.Assert(
                    test=ast.Compare(
                        left=ast.Constant(value=1),
                        ops=[ast.Eq()],
                        comparators=[
                            maybe_await(
                                ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Call(
                                            func=ast.Attribute(
                                                value=ast.Call(
                                                    func=ast.Attribute(
                                                        value=ast.Attribute(
                                                            value=ast.Name(
                                                                id=object_schema.title,
                                                                ctx=ast.Load(),
                                                            ),
                                                            attr='objects',
                                                            ctx=ast.Load(),
                                                        ),
                                                        attr='filter',
                                                        ctx=ast.Load(),
                                                    ),
                                                    args=[],
                                                    keywords=[
                                                        ast.keyword(
                                                            arg='_address__object_id',
                                                            value=ast.Attribute(
                                                                value=ast.Name(
                                                                    id='obj',
                                                                    ctx=ast.Load(),
                                                                ),
                                                                attr='object_id',
                                                                ctx=ast.Load(),
                                                            ),
                                                        )
                                                    ],
                                                ),
                                                attr='count',
                                                ctx=ast.Load(),
                                            ),
                                            args=[],
                                            keywords=[],
                                        ),
                                        attr=execute_name,
                                        ctx=ast.Load(),
                                    ),
                                    args=[],
                                    keywords=[],
                                )
                            )
                        ],
                    )
                ),
            ],
            decorator_list=test_function_decorator_list(),
            returns=ast.Constant(value=None),
            type_comment=None,
        )


def _update_test(
    model_name_snake_case: str,
    object_schema: ObjectSchema,
    models_dir: Path,
    test_data_type: TestDataType,
    cli_config: CliConfig,
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    if not object_schema.properties:
        msg = f'No properties found in the object schema for {rich_highlight(model_name_snake_case)}.'
        raise ValueError(msg)
    if AmsdalConfigManager().get_config().async_mode:
        save_name = 'asave'
    else:
        save_name = 'save'

    imports_set: set[tuple[str, str]] = set()
    object_create_expr = object_creation_call(
        model_name_snake_case,
        object_schema,
        models_dir,
        imports_set,
        test_data_type,
        cli_config=cli_config,
    )
    if sys.version_info >= (3, 12):
        return _function_def()(
            name=f'test_update_{model_name_snake_case}',
            args=test_function_arguments(),
            body=[
                *[ast.ImportFrom(module=module, names=[ast.alias(name=name)], level=0) for module, name in imports_set],
                _assert_state_count(0, object_schema.title),
                _assert_lakehouse_count(0, object_schema.title),
                ast.Assign(
                    targets=[
                        ast.Name(id='obj', ctx=ast.Store()),
                    ],
                    value=object_create_expr,
                ),
                _assert_state_count(1, object_schema.title),
                _assert_lakehouse_count(1, object_schema.title),
                *[
                    ast.Assign(
                        targets=[
                            ast.Attribute(
                                value=ast.Name(id='obj', ctx=ast.Load()),
                                attr=prop_name,
                                ctx=ast.Store(),
                            )
                        ],
                        value=generate_values_for_type_data(
                            prop_value,
                            models_dir,
                            imports_set,
                            test_data_type,
                            field_name=prop_name,
                            cli_config=cli_config,
                        ),
                    )
                    for prop_name, prop_value in object_schema.properties.items()
                ],
                ast.Expr(
                    value=maybe_await(
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='obj', ctx=ast.Load()),
                                attr=save_name,
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        )
                    )
                ),
                _assert_state_count(1, object_schema.title),
                _assert_lakehouse_count(2, object_schema.title),
            ],
            decorator_list=test_function_decorator_list(),
            returns=ast.Constant(value=None),
            type_comment=None,
            type_params=[],
        )
    else:
        return _function_def()(
            name=f'test_update_{model_name_snake_case}',
            args=test_function_arguments(),
            body=[
                *[ast.ImportFrom(module=module, names=[ast.alias(name=name)], level=0) for module, name in imports_set],
                _assert_state_count(0, object_schema.title),
                _assert_lakehouse_count(0, object_schema.title),
                ast.Assign(
                    targets=[
                        ast.Name(id='obj', ctx=ast.Store()),
                    ],
                    value=object_create_expr,
                ),
                _assert_state_count(1, object_schema.title),
                _assert_lakehouse_count(1, object_schema.title),
                *[
                    ast.Assign(
                        targets=[
                            ast.Attribute(
                                value=ast.Name(id='obj', ctx=ast.Load()),
                                attr=prop_name,
                                ctx=ast.Store(),
                            )
                        ],
                        value=generate_values_for_type_data(
                            prop_value,
                            models_dir,
                            imports_set,
                            test_data_type,
                            field_name=prop_name,
                            cli_config=cli_config,
                        ),
                    )
                    for prop_name, prop_value in object_schema.properties.items()
                ],
                ast.Expr(
                    value=maybe_await(
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='obj', ctx=ast.Load()),
                                attr=save_name,
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        )
                    )
                ),
                _assert_state_count(1, object_schema.title),
                _assert_lakehouse_count(2, object_schema.title),
            ],
            decorator_list=test_function_decorator_list(),
            returns=ast.Constant(value=None),
            type_comment=None,
        )


def _delete_test(
    model_name_snake_case: str,
    object_schema: ObjectSchema,
    models_dir: Path,
    test_data_type: TestDataType,
    cli_config: CliConfig,
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    if not object_schema.properties:
        msg = f'No properties found in the object schema for {rich_highlight(model_name_snake_case)}.'
        raise ValueError(msg)

    if AmsdalConfigManager().get_config().async_mode:
        delete_name = 'adelete'
    else:
        delete_name = 'delete'

    imports_set: set[tuple[str, str]] = set()
    object_create_expr = object_creation_call(
        model_name_snake_case,
        object_schema,
        models_dir,
        imports_set,
        test_data_type,
        cli_config=cli_config,
    )

    if sys.version_info >= (3, 12):
        return _function_def()(
            name=f'test_delete_{model_name_snake_case}',
            args=test_function_arguments(),
            body=[
                *[ast.ImportFrom(module=module, names=[ast.alias(name=name)], level=0) for module, name in imports_set],
                ast.Assign(
                    targets=[
                        ast.Name(id='obj', ctx=ast.Store()),
                    ],
                    value=object_create_expr,
                ),
                _assert_state_count(1, object_schema.title),
                _assert_lakehouse_count(1, object_schema.title),
                ast.Expr(
                    value=maybe_await(
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='obj', ctx=ast.Load()),
                                attr=delete_name,
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        )
                    )
                ),
                _assert_state_count(0, object_schema.title),
                _assert_lakehouse_count(2, object_schema.title),
            ],
            decorator_list=test_function_decorator_list(),
            returns=ast.Constant(value=None),
            type_comment=None,
            type_params=[],
        )
    else:
        return _function_def()(
            name=f'test_delete_{model_name_snake_case}',
            args=test_function_arguments(),
            body=[
                *[ast.ImportFrom(module=module, names=[ast.alias(name=name)], level=0) for module, name in imports_set],
                ast.Assign(
                    targets=[
                        ast.Name(id='obj', ctx=ast.Store()),
                    ],
                    value=object_create_expr,
                ),
                _assert_state_count(1, object_schema.title),
                _assert_lakehouse_count(1, object_schema.title),
                ast.Expr(
                    value=maybe_await(
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='obj', ctx=ast.Load()),
                                attr=delete_name,
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        )
                    )
                ),
                _assert_state_count(0, object_schema.title),
                _assert_lakehouse_count(2, object_schema.title),
            ],
            decorator_list=test_function_decorator_list(),
            returns=ast.Constant(value=None),
            type_comment=None,
        )


def generate_unit_tests(
    model_name: str,
    model_name_snake_case: str,
    cli_config: CliConfig,
    test_data_type: TestDataType,
) -> str:
    models_dir = cli_config.app_directory / cli_config.src_dir / 'models'

    object_schema = get_class_schema(models_dir, model_name, cli_config)

    # Create an empty module
    module = ast.Module(body=[], type_ignores=[])

    # Add necessary imports
    module.body.append(ast.Import(names=[ast.alias(name='pytest', asname=None)]))
    module.body.append(ast.Import(names=[ast.alias(name='datetime', asname=None)]))
    module.body.append(
        ast.ImportFrom(module='faker', names=[ast.alias(name='Faker')], level=0),
    )
    module.body.append(
        ast.ImportFrom(
            module='amsdal_models.querysets.executor',
            names=[ast.alias(name='LAKEHOUSE_DB_ALIAS')],
            level=0,
        ),
    )
    module.body.append(
        ast.Assign(
            targets=[ast.Name(id='FAKER', ctx=ast.Store())],
            value=ast.Call(func=ast.Name(id='Faker', ctx=ast.Load()), args=[], keywords=[]),
        ),
    )

    module.body.append(
        _create_test(
            model_name_snake_case,
            object_schema,
            models_dir,
            test_data_type=test_data_type,
            cli_config=cli_config,
        )
    )
    module.body.append(
        _update_test(
            model_name_snake_case,
            object_schema,
            models_dir,
            test_data_type=test_data_type,
            cli_config=cli_config,
        )
    )
    module.body.append(
        _delete_test(
            model_name_snake_case,
            object_schema,
            models_dir,
            test_data_type=test_data_type,
            cli_config=cli_config,
        )
    )

    return isort.code(
        black.format_str(
            astor.to_source(module),
            mode=black.FileMode(
                string_normalization=False,
                target_versions={TargetVersion.PY311},
                line_length=120,
            ),
        ),
        config=isort.Config(
            force_single_line=True,
            order_by_type=True,
            known_first_party=['amsdal_models', 'models'],
        ),
    )


def generate_and_save_unit_tests(
    model_name: str,
    cli_config: CliConfig,
    test_data_type: TestDataType,
) -> bool:
    model_name = classify(model_name)
    model_name_snake_case = to_snake_case(model_name)

    unit_test_dir = cli_config.app_directory / cli_config.src_dir / 'tests' / 'unit'
    unit_test_dir.mkdir(parents=True, exist_ok=True)

    filename = f'test_{model_name_snake_case}.py'
    test_file = unit_test_dir / filename

    if test_file.exists():
        if not CustomConfirm.ask(
            rich_info(f'Test file {rich_highlight(filename)} already exists. Do you want to overwrite it?'),
            default=False,
            show_default=False,
            choices=['y', 'N'],
        ):
            return False

    result_module = generate_unit_tests(model_name, model_name_snake_case, cli_config, test_data_type)

    with test_file.open('w') as f:
        f.write(result_module)

    return True
