from enum import Enum


class OutputFormat(str, Enum):
    """
    Output format for CLI commands.

    Attributes:
        default (str): Default output format.
        json (str): JSON output format.
        wide (str): Wide output format.
    """

    default = 'default'
    json = 'json'
    wide = 'wide'


class DBType(str, Enum):
    """
    Enumeration for database types.

    This enum defines the types of database available.

    Attributes:
        postgres (str): PostgreSQL database.
        sqlite (str): SQLite database.
    """

    postgres = 'postgres'
    sqlite = 'sqlite'
    csv = 'csv'
