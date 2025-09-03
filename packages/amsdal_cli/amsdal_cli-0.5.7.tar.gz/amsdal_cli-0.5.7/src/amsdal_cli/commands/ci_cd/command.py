from pathlib import Path

import typer
from rich import print as rprint

from amsdal_cli.app import app
from amsdal_cli.commands.ci_cd.constants import Vcs


@app.command(name='ci-cd')
def ci_cd_command(
    output: Path = typer.Argument('.', help='Path to output directory'),  # noqa: B008
    vcs: Vcs = typer.Option(Vcs.github, help='Version Control System'),  # noqa: B008
) -> None:
    """
    Generates CI/CD pipeline files for specified VCS.
    Currently supported VCS are GitHub.

    Example of usage:

    Generate CI/CD pipeline files for GitHub:
    ```bash
    amsdal ci-cd
    ```
    """
    from amsdal_cli.commands.ci_cd.constants import GITHUB_DETAILS
    from amsdal_cli.utils.text import rich_success

    template_dir = Path(__file__).parent / 'templates'

    if vcs == Vcs.github:
        pipeline_file = output / '.github' / 'workflows' / 'ci_cd.yml'
        pipeline_file.parent.mkdir(exist_ok=True, parents=True)
        pipeline_file.write_text(
            (template_dir / f'{vcs.value}.yml').read_text(),
        )
        rprint(rich_success('Done!'))
        rprint(GITHUB_DETAILS)
