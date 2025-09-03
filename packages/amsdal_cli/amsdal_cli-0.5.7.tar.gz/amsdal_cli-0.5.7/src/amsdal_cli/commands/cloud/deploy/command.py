from amsdal_cli.commands.cloud.app import cloud_sub_app
from amsdal_cli.commands.cloud.deploy.app import deploy_sub_app
from amsdal_cli.commands.cloud.deploy.sub_commands import *  # noqa

cloud_sub_app.add_typer(deploy_sub_app, name='deployments, deploys, ds')
