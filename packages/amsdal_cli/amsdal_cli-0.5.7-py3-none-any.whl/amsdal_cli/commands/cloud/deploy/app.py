import typer

from amsdal_cli.utils.alias_group import AliasGroup

deploy_sub_app = typer.Typer(
    help='Manage app deployments on the Cloud Server. Without sub-command, it lists the deployments.',
    cls=AliasGroup,
)
