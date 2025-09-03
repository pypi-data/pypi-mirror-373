from amsdal_cli.commands.cloud.secret.sub_commands.secret_delete import secret_delete_command
from amsdal_cli.commands.cloud.secret.sub_commands.secret_list import secret_list_callback
from amsdal_cli.commands.cloud.secret.sub_commands.secret_new import secret_add_command

__all__ = [
    'secret_add_command',
    'secret_delete_command',
    'secret_list_callback',
]
