import typer

from amsdal_cli.utils.alias_group import AliasGroup

basic_auth_sub_app = typer.Typer(
    help='Hide the API behind a Basic Auth',
    cls=AliasGroup,
)
