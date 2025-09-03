import typer

from amsdal_cli.utils.alias_group import AliasGroup

secret_sub_app = typer.Typer(
    help='Manage secrets for your Cloud Server app. Without any sub-command, it will list all secrets.',
    cls=AliasGroup,
)
