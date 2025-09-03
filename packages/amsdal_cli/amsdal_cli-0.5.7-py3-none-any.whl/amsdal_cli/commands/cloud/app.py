import typer

from amsdal_cli.utils.alias_group import AliasGroup

cloud_sub_app = typer.Typer(
    help='Commands to interact with the Cloud Server.',
    cls=AliasGroup,
)
