import typer

from amsdal_cli.utils.alias_group import AliasGroup

sub_app = typer.Typer(
    help="Generates application's files such as models, properties, transactions, etc.",
    cls=AliasGroup,
)
