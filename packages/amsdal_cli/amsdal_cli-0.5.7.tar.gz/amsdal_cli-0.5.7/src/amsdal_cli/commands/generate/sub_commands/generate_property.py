import typer
from rich import print as rprint

from amsdal_cli.commands.generate.app import sub_app


@sub_app.command(name='property, prop, pr')
def generate_property(
    ctx: typer.Context,
    property_name: str = typer.Argument(
        ...,
        help=(
            'The property name. Note, it will always transform the provided name to camel_case. Enter the name in '
            'camel_case in order to avoid any issues.'
        ),
    ),
    model: str = typer.Option(..., help='The model name. It should be provided in PascalCase.'),
) -> None:
    """
    Generates property file for specified model.
    """
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.commands.generate.utils.build_base_path import build_model_base_path
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.cli_config import ModelsFormat
    from amsdal_cli.utils.copier import copy_blueprint
    from amsdal_cli.utils.text import rich_error

    cli_config: CliConfig = ctx.meta['config']

    if cli_config.models_format == ModelsFormat.PY:
        rprint(rich_error('This command is not available for Python based models.'))
        raise typer.Exit

    base_path = build_model_base_path(ctx, model)
    name = to_snake_case(property_name)
    output_path = base_path / 'properties'

    copy_blueprint(
        source_file_path=cli_config.templates_path / 'property.pyt',
        destination_path=output_path,
        destination_name=f'{name}.py',
        context={
            'property_name': name,
        },
        confirm_overwriting=True,
    )
