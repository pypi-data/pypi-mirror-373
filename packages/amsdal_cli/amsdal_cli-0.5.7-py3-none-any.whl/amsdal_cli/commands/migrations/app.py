import typer

from amsdal_cli.utils.alias_group import AliasGroup

sub_app = typer.Typer(
    help=(
        'Commands to manage migrations. Without subcommand, it will show list of all migrations, '
        'which are applied and not applied including CORE and CONTRIB migrations.'
    ),
    cls=AliasGroup,
)
