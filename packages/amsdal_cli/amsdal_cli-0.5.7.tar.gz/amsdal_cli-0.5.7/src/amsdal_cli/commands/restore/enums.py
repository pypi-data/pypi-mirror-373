from enum import Enum


class RestoreType(str, Enum):
    """
    Restore type for CLI `restore` command.

    Attributes:
        MODELS (str): Restore models/schemas to src folder.
        STATE_DB (str): Restore state database from lakehouse one.
    """

    MODELS = 'models'
    STATE_DB = 'state_db'
