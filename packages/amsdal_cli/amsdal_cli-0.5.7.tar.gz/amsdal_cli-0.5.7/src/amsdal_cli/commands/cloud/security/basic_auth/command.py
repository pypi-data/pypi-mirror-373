from amsdal_cli.commands.cloud.security.app import security_sub_app
from amsdal_cli.commands.cloud.security.basic_auth.app import basic_auth_sub_app
from amsdal_cli.commands.cloud.security.basic_auth.sub_commands import *  # noqa

security_sub_app.add_typer(basic_auth_sub_app, name='basic-auth, basic_auth, bauth, ba')
