import asyncio
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

import typer

from amsdal_cli.app import app

if TYPE_CHECKING:
    from amsdal.manager import AsyncAmsdalManager

    from amsdal_cli.utils.cli_config import CliConfig


async def _async_serve(
    cli_config: 'CliConfig',
    app_source_path: Path,
    config_path: Path,
    *,
    apply_fixtures: bool,
) -> 'AsyncAmsdalManager':
    from amsdal_utils.lifecycle.consumer import LifecycleConsumer
    from amsdal_utils.lifecycle.enum import LifecycleEvent
    from amsdal_utils.lifecycle.producer import LifecycleProducer

    from amsdal_cli.commands.serve.utils import async_build_app_and_check_migrations

    amsdal_manager = await async_build_app_and_check_migrations(
        cli_config=cli_config,
        output_path=cli_config.app_directory,
        app_source_path=app_source_path,
        config_path=config_path,
        apply_fixtures=apply_fixtures,
        confirm_migrations=False,
    )

    try:

        class AmsdalInitConsumer(LifecycleConsumer):
            def on_event(self, *args: Any, **kwargs: Any) -> None:
                pass

            async def on_event_async(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                if not amsdal_manager._is_setup:
                    await amsdal_manager.setup()
                    await amsdal_manager.post_setup()  # type: ignore[call-arg, misc]

                if not amsdal_manager.is_authenticated:
                    amsdal_manager.authenticate()

                amsdal_manager.init_classes()

        LifecycleProducer.add_listener(
            LifecycleEvent.ON_SERVER_STARTUP,
            AmsdalInitConsumer,
            insert_first=True,
        )
        return amsdal_manager
    except Exception:
        await amsdal_manager.teardown()
        raise


@app.command(name='serve, srv, s')
def serve_command(
    ctx: typer.Context,
    *,
    cleanup: bool = typer.Option(
        True,
        help='Cleanup the generated models, warehouse and files after stopping',
    ),
    remove_warehouse_on_cleanup: bool = typer.Option(
        False,
        help='Remove the warehouse directory on cleanup',
    ),
    config: Optional[Path] = typer.Option(None, help='Path to custom config.yml file'),  # noqa: B008, UP007
    host: str = typer.Option('0.0.0.0', help='Host to run the server on'),  # noqa: S104
    port: Optional[int] = typer.Option(None, help='Port to run the server on'),  # noqa: UP007
    auto_reload: bool = typer.Option(
        False,
        help='Enable auto-reload of the server when files change',
    ),
    apply_fixtures: bool = typer.Option(
        True,
        help='Apply fixtures to the database',
    ),
) -> None:
    """
    Starts a test FastAPI server based on your app's models.
    """

    from amsdal_server.server import start
    from amsdal_utils.config.manager import AmsdalConfigManager
    from amsdal_utils.lifecycle.consumer import LifecycleConsumer
    from amsdal_utils.lifecycle.enum import LifecycleEvent
    from amsdal_utils.lifecycle.producer import LifecycleProducer

    from amsdal_cli.commands.serve.services.supervisor import Supervisor
    from amsdal_cli.commands.serve.utils import build_app_and_check_migrations
    from amsdal_cli.commands.serve.utils import cleanup_app
    from amsdal_cli.utils.cli_config import CliConfig

    cli_config: CliConfig = ctx.meta['config']
    app_source_path = cli_config.app_directory / cli_config.src_dir
    server_port = port or cli_config.http_port

    try:
        if auto_reload:
            supervisor = Supervisor(
                cli_config=cli_config,
                app_source_path=app_source_path,
                output_path=cli_config.app_directory,
                config_path=config or cli_config.config_path,
                host=host,
                port=server_port,
                apply_fixtures=apply_fixtures,
            )
            try:
                supervisor.run()
            finally:
                supervisor.wait()
        else:
            config_path = config or cli_config.config_path
            config_manager = AmsdalConfigManager()
            config_manager.load_config(config_path)

            if config_manager.get_config().async_mode:
                # need to run the async server in a separate event loop
                manager = asyncio.run(
                    _async_serve(
                        cli_config=cli_config,
                        app_source_path=app_source_path,
                        config_path=config_path,
                        apply_fixtures=apply_fixtures,
                    )
                )
                try:
                    start(
                        is_development_mode=False,
                        host=host,
                        port=server_port,
                    )
                finally:
                    asyncio.run(manager.teardown())
            else:
                amsdal_manager = build_app_and_check_migrations(
                    cli_config=cli_config,
                    output_path=cli_config.app_directory,
                    app_source_path=app_source_path,
                    config_path=config or cli_config.config_path,
                    apply_fixtures=apply_fixtures,
                    confirm_migrations=False,
                )

                class AmsdalInitConsumer(LifecycleConsumer):
                    def on_event(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                        if not amsdal_manager._is_setup:
                            amsdal_manager.setup()
                            amsdal_manager.post_setup()  # type: ignore[call-arg]

                        if not amsdal_manager.is_authenticated:
                            amsdal_manager.authenticate()

                        amsdal_manager.init_classes()

                    async def on_event_async(self, *args: Any, **kwargs: Any) -> None:
                        pass

                LifecycleProducer.add_listener(
                    LifecycleEvent.ON_SERVER_STARTUP,
                    AmsdalInitConsumer,
                    insert_first=True,
                )
                start(
                    is_development_mode=False,
                    host=host,
                    port=server_port,
                )
    finally:
        if cleanup:
            cleanup_app(output_path=cli_config.app_directory, remove_warehouse=remove_warehouse_on_cleanup)
