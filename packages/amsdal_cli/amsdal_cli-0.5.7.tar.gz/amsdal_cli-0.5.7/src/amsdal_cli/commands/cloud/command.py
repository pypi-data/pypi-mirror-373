from amsdal_cli.app import app
from amsdal_cli.commands.cloud.app import cloud_sub_app
from amsdal_cli.commands.cloud.dependency.command import *  # noqa
from amsdal_cli.commands.cloud.deploy.command import *  # noqa
from amsdal_cli.commands.cloud.environments.command import *  # noqa
from amsdal_cli.commands.cloud.secret.command import *  # noqa
from amsdal_cli.commands.cloud.security.command import *  # noqa
from amsdal_cli.commands.cloud.sub_commands import *  # noqa

app.add_typer(cloud_sub_app, name='cloud, cld')
