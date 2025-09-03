from pathlib import Path
from typing import Any

from jinja2 import Environment
from jinja2 import FileSystemLoader


def render(template_path: Path, context: dict[str, Any]) -> str:
    """
    Render a template with the given context.

    Args:
        template_path (Path): The path to the template file.
        context (dict[str, Any]): The context dictionary for rendering the template.

    Returns:
        str: The rendered template as a string.
    """
    env = Environment(loader=FileSystemLoader(template_path.parent))  # noqa: S701
    template = env.get_template(template_path.name)

    return template.render({'ctx': context})
