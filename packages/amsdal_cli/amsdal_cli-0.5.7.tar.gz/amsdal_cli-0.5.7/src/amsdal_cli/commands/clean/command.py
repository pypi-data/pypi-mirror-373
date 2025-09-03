from pathlib import Path

import typer
from rich import print as rprint

from amsdal_cli.app import app


@app.command(name='clean, cln')
def clean_command(
    output: Path = typer.Argument('.', help='Path to output directory'),  # noqa: B008
    *,
    remove_db: bool = typer.Option(False, '--remove-db', '-db', help='Remove local database?'),
) -> None:
    """
    Cleans project's folder by removing all generated files and optionally local database.

    Example of usage:

    1. Cleanup generated files without removing local database:
    ```bash
    amsdal clean
    ```

    2. Cleanup generated files and remove local database:
    ```bash
    amsdal clean --remove-db
    ```
    """
    from amsdal_cli.commands.serve.utils import cleanup_app
    from amsdal_cli.utils.text import rich_success

    cleanup_app(
        output_path=output,
        remove_warehouse=remove_db,
    )
    rprint(rich_success('Cleaned!'))
