from pathlib import Path

from amsdal_utils.config.manager import AmsdalConfigManager

from amsdal_cli.utils.cli_config import CliConfig

CURRENT_DIR = Path(__file__).parent


def create_conftest_if_not_exist(cli_config: CliConfig) -> None:
    test_dir = cli_config.app_directory / cli_config.src_dir / 'tests'
    test_dir.mkdir(parents=True, exist_ok=True)
    conftest_file_path = test_dir / 'conftest.py'

    if AmsdalConfigManager().get_config().async_mode:
        template_conftest_path = CURRENT_DIR / 'templates' / 'async' / 'conftest.py'
    else:
        template_conftest_path = CURRENT_DIR / 'templates' / 'sync' / 'conftest.py'

    if not conftest_file_path.exists():
        with template_conftest_path.open() as f:
            conftest_file_path.write_text(f.read())
