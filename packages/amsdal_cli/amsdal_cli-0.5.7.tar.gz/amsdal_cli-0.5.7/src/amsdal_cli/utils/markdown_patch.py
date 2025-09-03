import inspect
from collections.abc import Iterable

import click
from rich.console import group
from rich.markdown import Markdown
from rich.text import Text
from typer.core import MarkupMode
from typer.rich_utils import MARKUP_MODE_MARKDOWN
from typer.rich_utils import STYLE_HELPTEXT_FIRST_LINE
from typer.rich_utils import _make_rich_text


@group()
def get_custom_help_text(
    *,
    obj: click.Command | click.Group,
    markup_mode: MarkupMode,
) -> Iterable[Markdown | Text]:
    """
    Get custom help text for a Click command or group.

    Args:
        obj (click.Command | click.Group): The Click command or group object.
        markup_mode (MarkupMode): The markup mode to use for formatting the help text.

    Returns:
        Iterable[Markdown | Text]: An iterable of Markdown or Text objects representing the help text.
    """
    # Fetch and dedent the help text
    help_text = inspect.cleandoc(obj.help or '')

    # Trim off anything that comes after \f on its own line
    help_text = help_text.partition('\f')[0]

    # Get the first paragraph
    first_line = help_text.split('\n\n')[0]

    # Remove single linebreaks
    if markup_mode != MARKUP_MODE_MARKDOWN and not first_line.startswith('\b'):
        first_line = first_line.replace('\n', ' ')

    yield _make_rich_text(
        text=first_line.strip(),
        style=STYLE_HELPTEXT_FIRST_LINE,
        markup_mode=markup_mode,
    )

    # Get remaining lines, remove single line breaks and format as dim
    remaining_paragraphs = help_text.split('\n\n')[1:]
    if remaining_paragraphs:
        remaining_lines = inspect.cleandoc('\n\n'.join(remaining_paragraphs).replace('<br/>', '\\'))
        yield _make_rich_text(
            text=remaining_lines,
            style='cyan',
            markup_mode=markup_mode,
        )
