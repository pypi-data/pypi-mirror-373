import json

import typer

from amsdal_cli.commands.generate.app import sub_app


@sub_app.command(name='permission, p')
def generate_permission(
    ctx: typer.Context,
    model: str = typer.Option(..., help='The model name. It should be provided in PascalCase.'),
    *,
    create: bool = typer.Option(True, help="Generate 'create' permission."),
    read: bool = typer.Option(True, help="Generate 'read' permission."),
    update: bool = typer.Option(True, help="Generate 'update' permission."),
    delete: bool = typer.Option(True, help="Generate 'delete' permission."),
) -> None:
    """
    Generates permission fixture file for specified model.
    """
    from amsdal.manager import AmsdalManager
    from amsdal.manager import AsyncAmsdalManager
    from amsdal_utils.config.manager import AmsdalConfigManager
    from amsdal_utils.utils.text import to_snake_case

    from amsdal_cli.commands.generate.enums import FIXTURES
    from amsdal_cli.utils.cli_config import CliConfig
    from amsdal_cli.utils.copier import write_file

    cli_config: CliConfig = ctx.meta['config']
    config_manager = AmsdalConfigManager()
    config_manager.load_config(cli_config.config_path)
    amsdal_manager: AsyncAmsdalManager | AmsdalManager

    if config_manager.get_config().async_mode:
        amsdal_manager = AsyncAmsdalManager()
    else:
        amsdal_manager = AmsdalManager()

    amsdal_manager.pre_setup()
    model_snake_case = to_snake_case(model)
    expected_permissions = []

    for permission_needed, permission_name in [
        (create, 'create'),
        (read, 'read'),
        (update, 'update'),
        (delete, 'delete'),
    ]:
        if permission_needed:
            expected_permissions.append(
                {
                    'external_id': f'{model_snake_case}_{permission_name}',
                    'model': model,
                    'action': permission_name,
                }
            )

    base_path = cli_config.app_directory / cli_config.src_dir
    (base_path / FIXTURES).mkdir(parents=True, exist_ok=True)
    permissions_file = base_path / FIXTURES / f'{model_snake_case}_permissions.json'

    if permissions_file.exists():
        permission_fixtures = json.loads(permissions_file.read_text())

        if not permission_fixtures.get('Permission'):
            permission_fixtures['Permission'] = []

    else:
        permission_fixtures = {'Permission': []}

    for permission in expected_permissions:
        if permission not in permission_fixtures['Permission']:
            permission_fixtures['Permission'].append(permission)

    write_file(
        json.dumps(permission_fixtures, indent=cli_config.indent),
        destination_file_path=permissions_file,
        confirm_overwriting=False,
    )
