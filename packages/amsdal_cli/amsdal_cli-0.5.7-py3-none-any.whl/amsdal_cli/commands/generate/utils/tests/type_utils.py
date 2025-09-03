import ast
from datetime import date
from datetime import timezone
from pathlib import Path

import faker
from amsdal_utils.models.data_models.core import DictSchema
from amsdal_utils.models.data_models.core import LegacyDictSchema
from amsdal_utils.models.data_models.core import TypeData
from amsdal_utils.schemas.schema import ObjectSchema
from amsdal_utils.utils.text import classify
from amsdal_utils.utils.text import to_snake_case

from amsdal_cli.commands.generate.enums import TestDataType
from amsdal_cli.commands.generate.utils.tests.model_utils import get_class_schema
from amsdal_cli.commands.generate.utils.tests.model_utils import object_creation_call
from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.text import rich_highlight

FAKER = faker.Faker()


def _faker_call(method: str) -> ast.Call:
    return ast.Call(
        func=ast.Attribute(
            value=ast.Name(id='FAKER', ctx=ast.Load()),
            attr=method,
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )


def _generate_values_for_type(
    data_type: str,
    type_data: TypeData | None,
    models_dir: Path,
    imports_set: set[tuple[str, str]],
    test_data_type: TestDataType,
    cli_config: CliConfig,
    field_name: str | None = None,
) -> ast.expr:
    if data_type == 'string':
        if test_data_type == TestDataType.DUMMY:
            return ast.Constant(value='dummy_text')

        function_name = 'pystr'

        if field_name in ['first_name', 'firstname', 'name']:
            function_name = 'first_name'

        if field_name in ['last_name', 'lastname']:
            function_name = 'last_name'

        if field_name and 'email' in field_name:
            function_name = 'email'

        if field_name and 'phone' in field_name:
            function_name = 'phone_number'

        if field_name and 'address' in field_name:
            function_name = 'address'

        if field_name and 'city' in field_name:
            function_name = 'city'

        if field_name and 'country' in field_name:
            function_name = 'country'

        if field_name and 'state' in field_name:
            function_name = 'state'

        if field_name and ('zip' in field_name or 'postal' in field_name):
            function_name = 'zip_code'

        if field_name and 'company' in field_name:
            function_name = 'company'

        if test_data_type == TestDataType.RANDOM:
            return ast.Constant(value=getattr(FAKER, function_name)())
        if test_data_type == TestDataType.DYNAMIC:
            return _faker_call(function_name)

    elif data_type == 'integer':
        if test_data_type == TestDataType.DUMMY:
            return ast.Constant(value=1)

        function_name = 'random_int'

        if test_data_type == TestDataType.RANDOM:
            return ast.Constant(value=getattr(FAKER, function_name)())

        if test_data_type == TestDataType.DYNAMIC:
            return _faker_call(function_name)

    elif data_type == 'number':
        if test_data_type == TestDataType.DUMMY:
            return ast.Constant(value=1.0)

        function_name = 'pyfloat'

        if field_name and 'age' in field_name:
            function_name = 'random_int'

        if test_data_type == TestDataType.RANDOM:
            return ast.Constant(value=getattr(FAKER, function_name)())
        if test_data_type == TestDataType.DYNAMIC:
            return _faker_call(function_name)

    elif data_type == 'boolean':
        if test_data_type == TestDataType.DUMMY:
            return ast.Constant(value=True)

        if test_data_type == TestDataType.RANDOM:
            return ast.Constant(value=faker.Faker().pybool())
        if test_data_type == TestDataType.DYNAMIC:
            return _faker_call('pybool')

    elif data_type == 'datetime':
        if test_data_type == TestDataType.DUMMY:
            return ast.Constant(value='2023-01-01T00:00:00Z')

        if test_data_type == TestDataType.RANDOM:
            dt = FAKER.date_time(tzinfo=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            return ast.Constant(value=dt)  # type: ignore[arg-type]
        if test_data_type == TestDataType.DYNAMIC:
            return _faker_call('date_time')

    elif data_type == 'date':
        if test_data_type == TestDataType.DUMMY:
            return ast.Constant(value=date(2023, 1, 1))  # type: ignore[arg-type]

        if test_data_type == TestDataType.RANDOM:
            dt = FAKER.date_time(tzinfo=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            return ast.Constant(value=dt.date())  # type: ignore[arg-type]

        if test_data_type == TestDataType.DYNAMIC:
            return _faker_call('date')

    elif data_type == 'array':
        if not type_data:
            msg = 'Type data is required for array type.'
            raise ValueError(msg)
        items = type_data.items

        if isinstance(items, TypeData):
            return ast.List(
                elts=[
                    generate_values_for_type_data(
                        items,
                        models_dir,
                        imports_set,
                        test_data_type,
                        cli_config=cli_config,
                    )
                ]
            )

    elif data_type == 'dictionary':
        if not type_data:
            msg = 'Type data is required for dictionary type.'
            raise ValueError(msg)

        items = type_data.items

        if isinstance(items, DictSchema):
            return ast.Dict(
                keys=[
                    generate_values_for_type_data(
                        items.key,
                        models_dir,
                        imports_set,
                        test_data_type,
                        cli_config=cli_config,
                    )
                ],
                values=[
                    generate_values_for_type_data(
                        items.value,
                        models_dir,
                        imports_set,
                        test_data_type,
                        cli_config=cli_config,
                    )
                ],
            )
        elif isinstance(items, LegacyDictSchema):
            return ast.Dict(
                keys=[
                    _generate_values_for_type(
                        items.key_type,
                        None,
                        models_dir,
                        imports_set,
                        test_data_type,
                        cli_config=cli_config,
                    )
                ],
                values=[
                    _generate_values_for_type(
                        items.value_type,
                        None,
                        models_dir,
                        imports_set,
                        test_data_type,
                        cli_config=cli_config,
                    )
                ],
            )

    elif data_type == 'File':
        imports_set.add(('models.core.file', 'File'))

        return ast.Call(
            func=ast.Attribute(
                value=ast.Call(
                    func=ast.Name(id='File', ctx=ast.Load()),
                    args=[],
                    keywords=[
                        ast.keyword(arg='filename', value=ast.Constant(value='file.txt')),
                        ast.keyword(arg='data', value=ast.Constant(value=b'file content')),
                    ],
                ),
                attr='save',
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        )

    elif data_type[0].isupper():
        snake_case_name = to_snake_case(classify(data_type))
        object_class = get_class_schema(models_dir, data_type, cli_config)

        return object_creation_call(
            snake_case_name,
            object_class,
            models_dir,
            imports_set,
            test_data_type,
            cli_config=cli_config,
        )

    msg = f'Unsupported data type: {rich_highlight(data_type)}'
    raise ValueError(msg)


def generate_values_for_type_data(
    type_data: TypeData,
    models_dir: Path,
    imports_set: set[tuple[str, str]],
    test_data_type: TestDataType,
    cli_config: CliConfig,
    field_name: str | None = None,
) -> ast.expr:
    return _generate_values_for_type(
        data_type=type_data.type,
        type_data=type_data,
        models_dir=models_dir,
        imports_set=imports_set,
        test_data_type=test_data_type,
        field_name=field_name,
        cli_config=cli_config,
    )


def keywords_for_schema(
    schema: ObjectSchema,
    models_dir: Path,
    imports_set: set[tuple[str, str]],
    test_data_type: TestDataType,
    cli_config: CliConfig,
) -> list[ast.keyword]:
    if not schema.properties:
        return []

    keywords = []

    for prop_name, prop_value in schema.properties.items():
        value = generate_values_for_type_data(
            type_data=prop_value,
            models_dir=models_dir,
            imports_set=imports_set,
            test_data_type=test_data_type,
            field_name=prop_name,
            cli_config=cli_config,
        )
        keywords.append(ast.keyword(arg=prop_name, value=value))

    return keywords
