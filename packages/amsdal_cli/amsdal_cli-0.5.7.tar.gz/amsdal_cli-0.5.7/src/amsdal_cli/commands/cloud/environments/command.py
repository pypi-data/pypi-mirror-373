from amsdal_cli.commands.cloud.app import cloud_sub_app
from amsdal_cli.commands.cloud.environments.app import environment_sub_app
from amsdal_cli.commands.cloud.environments.sub_commands import *  # noqa

cloud_sub_app.add_typer(environment_sub_app, name='environments, envs, env')
