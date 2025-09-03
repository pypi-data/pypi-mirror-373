import importlib

import httpx
from rich import print as rprint

from amsdal_cli.utils.text import rich_command
from amsdal_cli.utils.text import rich_highlight_version


def check_latest_amsdal_version() -> None:
    """
    Check the latest version of AMSDAL modules and suggest upgrades if necessary.

    Returns:
        None
    """
    session = httpx.Client()

    modules_to_update: list[str] = []

    for amsdal_module in [
        'amsdal_utils',
        'amsdal_data',
        'amsdal_models',
        'amsdal',
        'amsdal_server',
        'amsdal_cli',
    ]:
        try:
            module = importlib.import_module(f'{amsdal_module}.__about__')
            current_version = module.__version__
            response = session.get(f'https://pypi.org/pypi/{amsdal_module}/json')
            latest_version = response.json()['info']['version']

            if current_version == latest_version:
                continue

            rprint(
                f'You are using {amsdal_module} version {rich_highlight_version(current_version)}, '
                f'however version {rich_highlight_version(latest_version)} is available.'
            )

            modules_to_update.append(amsdal_module)

        except ImportError:
            continue

    if modules_to_update:
        upgrade_command = 'pip install --upgrade ' + ' '.join(modules_to_update)
        rprint(f"You should consider upgrading via the '{rich_command(upgrade_command)}' command.")
