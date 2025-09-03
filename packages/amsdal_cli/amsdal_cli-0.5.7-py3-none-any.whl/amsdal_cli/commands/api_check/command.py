from pathlib import Path
from typing import Optional

import typer

from amsdal_cli.app import app
from amsdal_cli.commands.api_check.config import ApiCheckConfig
from amsdal_cli.commands.api_check.services.comparison import check
from amsdal_cli.commands.api_check.services.loader import load_operation_logs
from amsdal_cli.commands.api_check.services.runner import ApiRunner
from amsdal_cli.commands.api_check.services.storage import save


@app.command(name='api-check')
def api_check(
    target_url: str = typer.Argument(  # noqa: B008
        ...,
        help='Target API base URL to test',
    ),
    config_file: Path = typer.Option(  # noqa: B008
        Path('api-check-config.json'),
        '--config',
        '-c',
        help='Path to configuration file (YAML or JSON) with test cases and auth settings',
        exists=True,
    ),
    compare_url: Optional[str] = typer.Option(  # noqa: B008
        None,
        '--compare-url',
        help='Second API base URL to compare against',
    ),
    compare_logs: Optional[Path] = typer.Option(  # noqa: B008
        None,
        '--compare-logs',
        help='Path to existing logs file to compare against',
        exists=True,
    ),
    output_logs: Optional[Path] = typer.Option(  # noqa: B008
        None,
        '--output',
        '-o',
        help='Path to save output logs',
    ),
) -> None:
    """
    Run API tests against target URL and compare results with another endpoint or saved logs.

    The command requires a configuration file (in YAML or JSON format) that defines:
    - Test cases with inputs and expected outputs
    - Authentication settings
    - Endpoints to test

    Authentication can be configured using environment variables:
    - AMSDAL_API_CHECK_AUTHORIZATION: Authorization token
    - AMSDAL_API_CHECK_EMAIL: Email for authentication
    - AMSDAL_API_CHECK_PASSWORD: Password for authentication

    If the token is invalid and no credentials are provided, the command will exit with an error.

    Examples:

    1. Save logs to a file without comparison:
       ```
       amsdal api-check https://api.example.com --compare-url https://api.example.com --output logs.json
       ```
       This uses the same URL for both target and comparison, which skips the comparison
       but still runs the API checks and saves the logs.

    2. Compare a URL with previously saved logs:
       ```
       amsdal api-check https://api.example.com --compare-logs previous-logs.json
       ```
       This runs API checks against the target URL and compares the results with
       the logs stored in previous-logs.json.

    3. Compare two different URLs:
       ```
       amsdal api-check https://api-prod.example.com --compare-url https://api-staging.example.com
       ```
       This runs API checks against both URLs and compares the results.

    You can combine these options as needed:
       ```
       amsdal api-check https://api-prod.example.com --compare-url https://api-staging.example.com \
           --output comparison.json
       ```
       This compares the two URLs and also saves the logs from the target URL.
    """
    if not compare_url and not compare_logs:
        msg = 'Either --compare-url or --compare-logs must be provided'
        raise typer.BadParameter(msg)

    if compare_url and compare_logs:
        msg = 'Cannot use both --compare-url and --compare-logs simultaneously'
        raise typer.BadParameter(msg)

    # Load configuration using the class method
    config = ApiCheckConfig.load_from_file(config_file)

    # Create runner with the loaded config
    target_runner = ApiRunner(target_url, config)
    target_logs_data = target_runner.run()
    has_errors = False

    if compare_url != target_url:
        if compare_url:
            compare_runner = ApiRunner(compare_url, config)
            compare_logs_data = compare_runner.run()
        else:
            compare_logs_data = load_operation_logs(compare_logs)  # type: ignore[arg-type]

        has_errors = check(target_logs_data, compare_logs_data)

    if output_logs:
        save(target_logs_data, destination=output_logs)

    if has_errors:
        raise typer.Exit(code=1)
