import typer

from amsdal_cli.utils.alias_group import AliasGroup

security_sub_app = typer.Typer(
    help='Manage security of the Cloud Server app.',
    cls=AliasGroup,
)
