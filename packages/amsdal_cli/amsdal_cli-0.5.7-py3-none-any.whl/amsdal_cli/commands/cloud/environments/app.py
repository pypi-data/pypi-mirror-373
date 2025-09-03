import typer

from amsdal_cli.utils.alias_group import AliasGroup

environment_sub_app = typer.Typer(
    help='Manage environments of your Cloud Server app. Without any sub-command, it will list all environments.',
    cls=AliasGroup,
)
