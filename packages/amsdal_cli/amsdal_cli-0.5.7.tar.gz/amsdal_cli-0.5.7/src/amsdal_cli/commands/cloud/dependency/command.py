from amsdal_cli.commands.cloud.app import cloud_sub_app
from amsdal_cli.commands.cloud.dependency.app import dependency_sub_app
from amsdal_cli.commands.cloud.dependency.sub_commands import *  # noqa

cloud_sub_app.add_typer(dependency_sub_app, name='dependencies, deps')
