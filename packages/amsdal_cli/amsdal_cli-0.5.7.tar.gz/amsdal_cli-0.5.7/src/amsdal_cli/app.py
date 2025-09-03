import typer
import typer.rich_utils

from amsdal_cli.commands.callbacks import init_app_context
from amsdal_cli.utils.alias_group import AliasGroup
from amsdal_cli.utils.markdown_patch import get_custom_help_text

# patch typer to use custom help text
typer.rich_utils._get_help_text = get_custom_help_text

app = typer.Typer(
    name='amsdal',
    callback=init_app_context,
    invoke_without_command=True,
    rich_markup_mode='markdown',
    cls=AliasGroup,
)
