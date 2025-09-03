from amsdal_cli.app import app
from amsdal_cli.commands.generate.app import sub_app
from amsdal_cli.commands.generate.sub_commands import *  # noqa

app.add_typer(sub_app, name='generate, gen, g')
