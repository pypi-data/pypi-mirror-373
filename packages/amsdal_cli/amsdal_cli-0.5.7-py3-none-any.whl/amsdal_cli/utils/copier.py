from collections.abc import Callable
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import typer

from amsdal_cli.utils.render_template import render
from amsdal_cli.utils.text import CustomConfirm
from amsdal_cli.utils.text import rich_info

TEMPLATE_EXTENSIONS = {
    '.pyt': '.py',
}


def copy_blueprints_from_directory(
    source_path: Path,
    destination_path: Path,
    context: dict[str, Any],
) -> None:
    """
    Copy blueprints from the source directory to the destination directory.

    Args:
        source_path (Path): The path to the source directory containing blueprints.
        destination_path (Path): The path to the destination directory where blueprints will be copied.
        context (dict[str, Any]): The context dictionary for rendering templates.

    Returns:
        None
    """
    for file in walk(source_path):
        file_path = file.relative_to(source_path)
        destination_file_path = destination_path / _normalize_destination_file_ext(file_path)
        destination_file_path.parent.mkdir(parents=True, exist_ok=True)
        destination_file_path.write_text(render(file, context))


def copy_blueprint(
    source_file_path: Path,
    destination_path: Path,
    context: dict[str, Any],
    destination_name: str | None = None,
    *,
    confirm_overwriting: bool = True,
) -> None:
    """
    Copy a blueprint from the source file to the destination directory.

    Args:
        source_file_path (Path): The path to the source file containing the blueprint.
        destination_path (Path): The path to the destination directory where the blueprint will be copied.
        context (dict[str, Any]): The context dictionary for rendering templates.
        destination_name (str, optional): The name of the destination file. Defaults to None.
        confirm_overwriting (bool, optional): Flag to confirm overwriting existing files. Defaults to True.

    Returns:
        None
    """
    destination_name = destination_name or source_file_path.name
    destination_file_path = destination_path / _normalize_destination_file_ext(Path(destination_name))

    write_file(
        render(source_file_path, context),
        destination_file_path,
        confirm_overwriting=confirm_overwriting,
    )


def write_file(
    content: str,
    destination_file_path: Path,
    *,
    confirm_overwriting: bool = True,
) -> None:
    """
    Write content to a file, optionally confirming overwriting if the file already exists.

    Args:
        content (str): The content to write to the file.
        destination_file_path (Path): The path to the destination file.
        confirm_overwriting (bool, optional): Flag to confirm overwriting existing files. Defaults to True.

    Returns:
        None
    """
    if (
        destination_file_path.exists()
        and confirm_overwriting
        and not CustomConfirm.ask(
            rich_info(f'The file "{destination_file_path.resolve()}" already exists. Would you like to overwrite it?'),
            default=False,
            show_default=False,
            choices=['y', 'N'],
        )
    ):
        raise typer.Exit

    destination_file_path.parent.mkdir(parents=True, exist_ok=True)
    destination_file_path.write_text(content)


def append_to_file(
    target_file: Path,
    destination_file: Path,
    transform: Callable[[str], str] | None = None,
) -> None:
    """
    Append the content of the target file to the destination file, optionally transforming the content.

    Args:
        target_file (Path): The path to the target file whose content will be appended.
        destination_file (Path): The path to the destination file where the content will be appended.
        transform (Callable[[str], str], optional): A function to transform the content before appending.
            Defaults to None.

    Returns:
        None
    """
    destination_file.parent.mkdir(parents=True, exist_ok=True)
    is_destination_exists = destination_file.exists()

    with (
        target_file.open('rt') as _target_file,
        destination_file.open('at') as _destination_file,
    ):
        if is_destination_exists:
            _destination_file.write('\n')

        content = _target_file.read()

        if transform:
            content = transform(content)

        _destination_file.write(content)
        _destination_file.write('\n')


def walk(path: Path) -> Iterator[Any]:
    """
    Recursively walk through a directory and yield file paths.

    Args:
        path (Path): The path to the directory to walk through.

    Returns:
        Iterator[Any]: An iterator over the file paths in the directory.
    """
    if not path.exists():
        return

    for item in path.iterdir():
        if item.is_dir():
            yield from walk(item)
            continue
        yield item


def _normalize_destination_file_ext(file_name: Path) -> Path:
    for ext_tmpl, ext in TEMPLATE_EXTENSIONS.items():
        if file_name.name.endswith(ext_tmpl):
            return file_name.with_name(file_name.name.replace(ext_tmpl, ext))
    return file_name
