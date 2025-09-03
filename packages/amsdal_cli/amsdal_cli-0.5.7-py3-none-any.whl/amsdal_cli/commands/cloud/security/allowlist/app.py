import typer

from amsdal_cli.utils.alias_group import AliasGroup

allowlist_sub_app = typer.Typer(
    help='Control who can access the API',
    cls=AliasGroup,
)
