from amsdal_cli.commands.cloud.app import cloud_sub_app
from amsdal_cli.commands.cloud.secret.app import secret_sub_app
from amsdal_cli.commands.cloud.secret.sub_commands import *  # noqa

cloud_sub_app.add_typer(secret_sub_app, name='secrets, sec, s')
