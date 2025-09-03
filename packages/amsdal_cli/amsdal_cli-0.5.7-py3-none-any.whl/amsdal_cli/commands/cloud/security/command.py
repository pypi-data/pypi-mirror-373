from amsdal_cli.commands.cloud.app import cloud_sub_app
from amsdal_cli.commands.cloud.security.allowlist.command import *  # noqa
from amsdal_cli.commands.cloud.security.app import security_sub_app
from amsdal_cli.commands.cloud.security.basic_auth.command import *  # noqa

cloud_sub_app.add_typer(security_sub_app, name='security')
