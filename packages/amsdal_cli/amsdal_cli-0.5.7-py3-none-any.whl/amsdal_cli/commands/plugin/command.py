import random
import shutil
import string
import uuid
from pathlib import Path
from typing import Annotated
from typing import Any

import typer
from rich import print as rprint

from amsdal_cli.app import app
from amsdal_cli.utils.cli_config import ModelsFormat


@app.command(name='plugin')
def plugin_command(
    plugin_name: str = typer.Argument(
        ...,
        help='The Plugin name. For example: MyPlugin',
    ),
    output_path: Path = typer.Argument(  # noqa: B008
        ...,
        help='Output path, where the plugin will be created.',
    ),
    *,
    models_format: Annotated[
        ModelsFormat,
        typer.Option(help='The format of models used in this plugin.'),
    ] = ModelsFormat.PY,
    is_async_mode: Annotated[
        bool,
        typer.Option('--async', help='Whether to run the plugin in async mode.'),
    ] = False,
) -> None:
    """
    Generates a new AMSDAL plugin.

    Example:

    ```bash
    amsdal plugin MyPlugin .
    ```

    It will create `my_plugin` directory in the current directory with AMSDAL plugin structure.
    """
    from amsdal.__about__ import __version__ as amsdal_version
    from amsdal_utils.utils.text import slugify
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.utils.copier import copy_blueprints_from_directory
    from amsdal_cli.utils.text import rich_error
    from amsdal_cli.utils.text import rich_success

    if not output_path.exists():
        rprint(rich_error(f'The output path "{output_path.resolve()}" does not exist.'))
        raise typer.Exit

    if output_path.is_file():
        rprint(rich_error(f'The output path "{output_path.resolve()}" is not a directory.'))
        raise typer.Exit

    output_path /= to_snake_case(plugin_name)

    if output_path.exists():
        if output_path.is_file():
            rprint(rich_error(f'The path "{output_path.resolve()}" is not a directory.'))
            raise typer.Exit

        if any(output_path.iterdir()):
            rprint(rich_error(f'The directory "{output_path.resolve()}" is not empty.'))
            raise typer.Exit

    application_uuid = (random.choice(string.ascii_lowercase) + uuid.uuid4().hex[:31]).lower()  # noqa: S311

    src_dir = plugin_name.strip().lower().replace(' ', '_').replace('-', '_')
    context = {
        'src_dir': src_dir,
        'application_uuid': application_uuid,
        'plugin_name': plugin_name,
        'plugin_name_slugify': slugify(plugin_name),
        'plugin_name_snake': to_snake_case(plugin_name),
        'amsdal_version': amsdal_version,
        'state_backend': 'sqlite-state-async' if is_async_mode else 'sqlite-state',
        'historical_backend': 'sqlite-historical-async' if is_async_mode else 'sqlite-historical',
        'models_format': models_format.value,
        'is_async_mode': is_async_mode,
    }

    copy_blueprints_from_directory(
        source_path=Path(__file__).parent / 'templates',
        destination_path=output_path,
        context=context,
    )
    # move src to src_dir
    shutil.move(str(output_path / 'src'), str(output_path / src_dir))
    (output_path / src_dir).mkdir(exist_ok=True)

    # Create example model based on format
    _create_example_model(output_path, models_format, context, src_dir=src_dir)

    rprint(rich_success(f'The plugin is successfully created in {output_path.resolve()}'))


def _create_example_model(
    output_path: Path,
    models_format: ModelsFormat,
    context: dict[str, Any],
    src_dir: str,
) -> None:
    """Create an example model based on the specified format."""
    from amsdal_cli.utils.copier import write_file

    models_dir = output_path / src_dir / 'models'

    if models_format == ModelsFormat.JSON:
        # Create JSON model
        model_dir = models_dir / 'example_model'
        model_dir.mkdir(exist_ok=True)

        json_content = """{
    "title": "ExampleModel",
    "type": "object",
    "properties": {
        "name": {
            "title": "name",
            "type": "string"
        },
        "description": {
            "title": "description",
            "type": "string"
        },
        "is_active": {
            "title": "is_active",
            "type": "boolean",
            "default": true
        }
    },
    "required": [
        "name"
    ],
    "indexed": [
        "name"
    ]
}"""
        write_file(json_content, model_dir / 'model.json', confirm_overwriting=False)
    else:
        # Create Python model
        py_content = f"""from amsdal_models.classes.model import Model
from amsdal_utils.models.enums import ModuleType
from pydantic.fields import Field


class ExampleModel(Model):
    \"\"\"Example model for {context['plugin_name']} plugin.\"\"\"

    __module_type__ = ModuleType.CONTRIB

    name: str = Field(..., index=True)
    description: str = Field(default="")
    is_active: bool = Field(default=True)
"""
        write_file(py_content, models_dir / 'example_model.py', confirm_overwriting=False)
