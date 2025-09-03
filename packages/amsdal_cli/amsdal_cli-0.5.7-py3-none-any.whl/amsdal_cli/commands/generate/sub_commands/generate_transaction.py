import typer

from amsdal_cli.commands.generate.app import sub_app


@sub_app.command(name='transaction, tr, t')
def generate_transaction(
    ctx: typer.Context,
    transaction_name: str = typer.Argument(
        ...,
        help=(
            'The transaction name. Note, it will always transform the provided name to camel_case. Enter the name in '
            'camel_case in order to avoid any issues.'
        ),
    ),
) -> None:
    """
    Generates transaction file with specified name.
    """
    from amsdal_utils.config.manager import AmsdalConfigManager
    from amsdal_utils.utils.text import classify
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.copier import copy_blueprint

    cli_config: CliConfig = ctx.meta['config']
    config_path = cli_config.config_path
    name = to_snake_case(transaction_name)
    output_path = cli_config.app_directory / cli_config.src_dir / 'transactions'
    config_manager = AmsdalConfigManager()
    config_manager.load_config(config_path)

    if AmsdalConfigManager().get_config().async_mode:
        template_name = 'async_transaction.pyt'
    else:
        template_name = 'transaction.pyt'

    copy_blueprint(
        source_file_path=cli_config.templates_path / template_name,
        destination_path=output_path,
        destination_name=f'{name}.py',
        context={
            'transaction_method_name': name,
            'transaction_class_name': classify(transaction_name),
        },
        confirm_overwriting=True,
    )
