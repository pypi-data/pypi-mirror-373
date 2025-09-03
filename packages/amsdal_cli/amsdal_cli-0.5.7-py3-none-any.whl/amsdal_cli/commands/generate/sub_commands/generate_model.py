import json
import sys
from typing import Any

import typer

from amsdal_cli.commands.generate.app import sub_app


@sub_app.command(name='model, mdl, md')
def generate_model(
    ctx: typer.Context,
    model_name: str = typer.Argument(
        ...,
        help='The model name. It should be provided in PascalCase.',
    ),
    attrs: list[str] = typer.Option(  # noqa: B008
        (None,),
        '--attributes',
        '-attrs',
    ),
    unique: list[str] = typer.Option(  # noqa: B008
        (None,),
        '--unique',
        '-u',
    ),
) -> None:
    """Generates model file.

    Example of usage:

    ```bash
    amsdal generate model UserProfile -attrs "name:string email:string:index age:number:default=18"
    ```

    So the format of attribute definition is: `<name>:<type>[:<options>]`

    Supported types:

    - string - Example: `position:string`
    - number - Example: `age:number`
    - boolean - Example: `is_active:boolean`
    - dict - Example: `metadata:dict:string:Country` (equivalent to `metadata: dict[str, Country]` in Python)
    - belongs-to - Example: `user:belongs-to:User` (equivalent to `user: User` in Python)
    - has-many - Example: `posts:has-many:Post` (equivalent to `posts: list[Post]` in Python)

    Where "belongs-to" and "has-many" are used to define the relationship between models. The "belongs-to" type is used
    to define the relationship where the model has a reference to another model. The "has-many" type is used to define
    the relationship where the model has a list of references to another model.

    The options are:

    * index - to mark the attribute as indexed. Example: `email:string:index`
    * unique - to mark the attribute as unique. Example: `email:string:unique`
    * required - to mark the attribute as required. Example: `email:string:required`
    * default - to set the default value for the attribute. It should be provided in the format: `default=<value>`.
    Example: `age:number:default=18 name:string:default=Developer`
    In order to put multi-word default values, you should use quotes. Example:

    ```bash
    amsdal generate model Person -attrs "name:string:default='John Doe'"
    ```

    Note, `dict` type does not support default value due to its complex structure.

    The options can be combined. Examples:
    - `email:string:unique:required`
    - `meta:dict:string:string:required:unique`
    - `age:number:default=18:required`
    - `name:string:default='John Doe':required`

     The ordering of the options does not matter.
    """
    from amsdal_utils.utils.text import classify
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.commands.generate.enums import MODEL_JSON_FILE
    from amsdal_cli.commands.generate.utils.model_attributes import parse_attributes
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.cli_config import ModelsFormat
    from amsdal_cli.utils.copier import write_file

    cli_config: CliConfig = ctx.meta['config']
    model_name = classify(model_name)
    name = to_snake_case(model_name)

    parsed_attrs = parse_attributes(attrs)

    json_schema: dict[str, Any] = {
        'title': model_name,
        'type': 'object',
        'properties': {},
        'required': [attr.name for attr in parsed_attrs if attr.required],
        'indexed': [attr.name for attr in parsed_attrs if attr.index],
    }

    unique_attrs: list[tuple[str, ...]] = [(attr.name,) for attr in parsed_attrs if attr.unique]

    for _unique in filter(None, unique):
        _unique_attrs = tuple(map(str.strip, _unique.split(',')))

        if _unique_attrs not in unique_attrs:
            unique_attrs.append(_unique_attrs)

    if unique_attrs:
        _unique = json_schema.setdefault('unique', [])
        _unique.extend(unique_attrs)

    for attr in parsed_attrs:
        property_info: dict[str, Any] = {
            'title': attr.name,
            'type': attr.json_type,
        }

        if attr.has_items:
            property_info['items'] = attr.json_items

        if attr.default != attr.NotSet:
            property_info['default'] = attr.default

        json_schema['properties'][attr.name] = property_info

    if cli_config.models_format == ModelsFormat.JSON:
        output_path = cli_config.app_directory / cli_config.src_dir / 'models' / name

        write_file(
            json.dumps(json_schema, indent=cli_config.indent),
            destination_file_path=output_path / MODEL_JSON_FILE,
            confirm_overwriting=True,
        )

    elif cli_config.models_format == ModelsFormat.PY:
        from amsdal.configs.main import settings
        from amsdal_models.builder.services.class_builder import ClassBuilder
        from amsdal_utils.models.enums import ModuleType
        from amsdal_utils.schemas.schema import ObjectSchema

        from amsdal_cli.utils.schema_repository import build_schema_repository

        output_path = cli_config.app_directory / cli_config.src_dir / 'models'
        output_path.mkdir(exist_ok=True, parents=True)
        (output_path / '__init__.py').touch(exist_ok=True)

        sys.path.insert(0, str((cli_config.app_directory / cli_config.src_dir).absolute()))

        schema_repository = build_schema_repository(cli_config=cli_config)
        class_builder = ClassBuilder()

        class_builder.build(
            models_package_path=output_path,
            models_module_path=settings.USER_MODELS_MODULE,
            object_schema=ObjectSchema(**json_schema),
            module_type=ModuleType.CONTRIB if cli_config.is_plugin else ModuleType.USER,
            dependencies=schema_repository.model_module_info,  # type: ignore[arg-type]
            indent_width=' ' * cli_config.indent,
        )
    else:
        msg = f'This models format "{cli_config.models_format} does not supported now!'
        raise ValueError(msg)
