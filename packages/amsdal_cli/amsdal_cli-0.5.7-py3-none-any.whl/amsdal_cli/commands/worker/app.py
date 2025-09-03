import typer

from amsdal_cli.utils.alias_group import AliasGroup

sub_app = typer.Typer(
    help='Commands to run worker.',
    cls=AliasGroup,
)
