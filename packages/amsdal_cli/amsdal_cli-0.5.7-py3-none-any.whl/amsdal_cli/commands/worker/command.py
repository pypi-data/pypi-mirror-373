from amsdal_cli.app import app
from amsdal_cli.commands.worker.app import sub_app
from amsdal_cli.commands.worker.sub_commands import *  # noqa

app.add_typer(sub_app, name='worker, w')
