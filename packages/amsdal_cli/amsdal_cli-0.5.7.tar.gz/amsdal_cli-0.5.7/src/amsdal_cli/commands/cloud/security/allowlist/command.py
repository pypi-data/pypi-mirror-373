from amsdal_cli.commands.cloud.security.allowlist.app import allowlist_sub_app
from amsdal_cli.commands.cloud.security.allowlist.sub_commands import *  # noqa
from amsdal_cli.commands.cloud.security.app import security_sub_app

security_sub_app.add_typer(allowlist_sub_app, name='allowlist, alist, al')
