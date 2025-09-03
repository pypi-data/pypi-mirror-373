import typer
from rich import print as rprint

from amsdal_cli.commands.generate.app import sub_app
from amsdal_cli.commands.generate.enums import HookName


@sub_app.command(name='hook, hk, h')
def generate_hook(
    ctx: typer.Context,
    hook_name: HookName = typer.Argument(  # noqa: B008
        ...,
        help='The hook name.',
    ),
    model: str = typer.Option(..., help='The model name. It should be provided in PascalCase.'),
) -> None:
    """
    Generates hook file for specified model.
    """
    from amsdal_utils.config.manager import AmsdalConfigManager

    from amsdal_cli.commands.generate.utils.build_base_path import build_model_base_path
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.cli_config import ModelsFormat
    from amsdal_cli.utils.copier import copy_blueprint
    from amsdal_cli.utils.text import rich_error

    cli_config: CliConfig = ctx.meta['config']

    if cli_config.models_format == ModelsFormat.PY:
        rprint(rich_error('This command is not available for Python based models.'))
        raise typer.Exit

    base_path = build_model_base_path(ctx, model)
    output_path = base_path / 'hooks'
    config_manager = AmsdalConfigManager()
    config_manager.load_config(cli_config.config_path)
    is_async = AmsdalConfigManager().get_config().async_mode

    copy_blueprint(
        source_file_path=cli_config.templates_path / 'hook.pyt',
        destination_path=output_path,
        destination_name=f'{hook_name.value}.py',
        context={
            'hook_name': hook_name.value,
            'is_init': hook_name in (HookName.PRE_INIT, HookName.POST_INIT),
            'is_async': is_async,
        },
        confirm_overwriting=True,
    )
