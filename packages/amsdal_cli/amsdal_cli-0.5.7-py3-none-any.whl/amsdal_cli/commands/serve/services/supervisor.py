import logging
import multiprocessing
from collections.abc import Callable
from dataclasses import dataclass
from multiprocessing.context import SpawnProcess
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeAlias

from amsdal.configs.main import settings
from amsdal.errors import AmsdalAuthConnectionError
from amsdal.errors import AmsdalCloudError
from amsdal.errors import AmsdalRuntimeError
from amsdal.errors import AmsdalSignupError
from amsdal.manager import AmsdalManager
from amsdal_models.classes.class_manager import ClassManager
from amsdal_server.server import start
from amsdal_utils.classes.version_manager import ClassVersionManager
from amsdal_utils.config.manager import AmsdalConfigManager
from rich import print as rprint
from watchfiles import run_process
from watchfiles.filters import PythonFilter

from amsdal_cli.commands.build.services.builder import AppBuilder
from amsdal_cli.commands.serve.filters.models_watch_filter import ModelsWatchFilter
from amsdal_cli.commands.serve.filters.static_files_watch_filter import StaticFilesWatchFilter
from amsdal_cli.commands.serve.utils import build_app_and_check_migrations
from amsdal_cli.utils.cli_config import CliConfig
from amsdal_cli.utils.text import rich_error
from amsdal_cli.utils.text import rich_info
from amsdal_cli.utils.text import rich_success
from amsdal_cli.utils.text import rich_warning

spawn_context = multiprocessing.get_context('spawn')

START_SERVER_EVENT = 'start_server'
STOP_SERVER_EVENT = 'stop_server'

if TYPE_CHECKING:
    QueueType: TypeAlias = multiprocessing.Queue[str]
else:
    QueueType: TypeAlias = multiprocessing.Queue


@dataclass
class ProcessState:
    """
    Represents the state of various processes in the application.

    Attributes:
        server (SpawnProcess | None): The server process.
        watch_models (SpawnProcess | None): The process watching model changes.
        watch_static_files (SpawnProcess | None): The process watching static file changes.
        watch_fixtures (SpawnProcess | None): The process watching fixture changes.
        watch_transactions (SpawnProcess | None): The process watching transaction changes.
    """

    server: SpawnProcess | None = None
    watch_models: SpawnProcess | None = None
    watch_static_files: SpawnProcess | None = None
    watch_fixtures: SpawnProcess | None = None
    watch_transactions: SpawnProcess | None = None


class Supervisor:
    def __init__(
        self,
        cli_config: CliConfig,
        app_source_path: Path,
        output_path: Path,
        config_path: Path,
        host: str,
        port: int,
        *,
        apply_fixtures: bool,
    ) -> None:
        self._cli_config = cli_config
        self._app_source_path: Path = app_source_path
        self._output_path: Path = output_path
        self._config_path: Path = config_path
        self._process_state: ProcessState = ProcessState()
        self._queue: QueueType = spawn_context.Queue()

        self._host: str = host
        self._port: int = port
        self._apply_fixtures: bool = apply_fixtures

    def run(self) -> None:
        try:
            if not self.start():
                return

            while True:
                sleep(0.1)
        except Exception as exc:
            logging.exception('Error while running the server: %s', exc, exc_info=True)
            self.stop()
        except KeyboardInterrupt:
            self.stop()

    def start(self) -> bool:
        build_app_and_check_migrations(
            cli_config=self._cli_config,
            output_path=self._output_path,
            app_source_path=self._app_source_path,
            config_path=self._config_path,
            apply_fixtures=False,
            confirm_migrations=True,
        )

        try:
            manager = AmsdalManager(raise_on_new_signup=True)
            manager.authenticate()
        except AmsdalSignupError:
            rprint(rich_warning('Please set credential variables before next AMSDAL run'))
            return False
        except AmsdalAuthConnectionError:
            rprint(rich_error('Cannot connect to AMSDAL authentication service. Please try again in a moment.'))
            return False
        except AmsdalCloudError as e:
            rprint(rich_error(f'{e}'))
            return False

        self._process_state.server = self._run_server(
            self._queue,
            self._output_path,
            self._config_path,
            self._host,
            self._port,
        )
        self._process_state.watch_models = self._run_watch_models(
            self._queue,
            self._cli_config,
            self._app_source_path,
            self._output_path,
            self._config_path,
            apply_fixtures=self._apply_fixtures,
        )
        self._process_state.watch_static_files = self._run_watch_static_files(
            self._cli_config,
            self._app_source_path,
            self._output_path,
            self._config_path,
        )
        self._process_state.watch_transactions = self._run_watch_transactions(
            self._cli_config,
            self._app_source_path,
            self._output_path,
            self._config_path,
        )

        return True

    def stop(self) -> None:
        if self._process_state.server is not None and self._process_state.server.is_alive():
            self._process_state.server.terminate()

        if self._process_state.watch_models is not None and self._process_state.watch_models.is_alive():
            self._process_state.watch_models.terminate()

        if self._process_state.watch_static_files is not None and self._process_state.watch_static_files.is_alive():
            self._process_state.watch_static_files.terminate()

        if self._process_state.watch_transactions is not None and self._process_state.watch_transactions.is_alive():
            self._process_state.watch_transactions.terminate()

    def wait(self) -> None:
        if self._process_state.server is not None and self._process_state.server.is_alive():
            self._process_state.server.join()

        if self._process_state.watch_models is not None and self._process_state.watch_models.is_alive():
            self._process_state.watch_models.join()

        if self._process_state.watch_static_files is not None and self._process_state.watch_static_files.is_alive():
            self._process_state.watch_static_files.join()

        if self._process_state.watch_transactions is not None and self._process_state.watch_transactions.is_alive():
            self._process_state.watch_transactions.join()

    @classmethod
    def _run_server(
        cls,
        queue: QueueType,
        output_path: Path,
        config_path: Path,
        host: str,
        port: int,
    ) -> SpawnProcess:
        process = spawn_context.Process(
            target=cls._check_and_serve,
            kwargs={
                'queue': queue,
                'is_development_mode': False,
                'output_path': output_path,
                'config_path': config_path,
                'host': host,
                'port': port,
            },
        )
        process.start()

        return process

    @classmethod
    def _check_and_serve(
        cls,
        queue: QueueType,
        *,
        is_development_mode: bool,
        output_path: Path,
        config_path: Path,
        host: str,
        port: int,
    ) -> None:
        _server_process: SpawnProcess | None = None

        try:
            while True:
                event = queue.get()
                if event == STOP_SERVER_EVENT:
                    if _server_process is not None and _server_process.is_alive():
                        _server_process.terminate()
                elif event == START_SERVER_EVENT:
                    _server_process = spawn_context.Process(
                        target=cls._serve,
                        kwargs={
                            'is_development_mode': is_development_mode,
                            'output_path': output_path,
                            'config_path': config_path,
                            'host': host,
                            'port': port,
                        },
                    )
                    _server_process.start()
        except KeyboardInterrupt:
            if _server_process is not None and _server_process.is_alive():
                _server_process.terminate()

    @classmethod
    def _run_watch_models(
        cls,
        queue: QueueType,
        cli_config: CliConfig,
        app_source_path: Path,
        output_path: Path,
        config_path: Path,
        *,
        apply_fixtures: bool,
    ) -> SpawnProcess:
        process = spawn_context.Process(
            target=cls._watch,
            args=(
                'ModelsWatch',
                app_source_path / 'models',
            ),
            kwargs={
                'target': cls._build_models_and_migrate,
                'kwargs': {
                    'queue': queue,
                    'cli_config': cli_config,
                    'app_source_path': app_source_path,
                    'output_path': output_path,
                    'config_path': config_path,
                    'apply_fixtures': apply_fixtures,
                },
                'watch_filter': ModelsWatchFilter(),
            },
        )
        process.start()

        return process

    @classmethod
    def _run_watch_static_files(
        cls,
        cli_config: CliConfig,
        app_source_path: Path,
        output_path: Path,
        config_path: Path,
    ) -> SpawnProcess:
        process = spawn_context.Process(
            target=cls._watch,
            args=(
                'StaticFilesWatch',
                app_source_path,
            ),
            kwargs={
                'target': cls._build_static_files,
                'kwargs': {
                    'cli_config': cli_config,
                    'app_source_path': app_source_path,
                    'output_path': output_path,
                    'config_path': config_path,
                },
                'watch_filter': StaticFilesWatchFilter(),
            },
        )
        process.start()

        return process

    @classmethod
    def _run_watch_transactions(
        cls,
        cli_config: CliConfig,
        app_source_path: Path,
        output_path: Path,
        config_path: Path,
    ) -> SpawnProcess:
        process = spawn_context.Process(
            target=cls._watch,
            args=(
                'TransactionsWatch',
                app_source_path / 'transactions',
            ),
            kwargs={
                'target': cls._build_transactions,
                'kwargs': {
                    'cli_config': cli_config,
                    'app_source_path': app_source_path,
                    'output_path': output_path,
                    'config_path': config_path,
                },
                'watch_filter': PythonFilter(),
            },
        )
        process.start()

        return process

    @classmethod
    def _serve(
        cls,
        output_path: Path,
        config_path: Path,
        **kwargs: Any,
    ) -> None:
        from amsdal_utils.lifecycle.consumer import LifecycleConsumer
        from amsdal_utils.lifecycle.enum import LifecycleEvent
        from amsdal_utils.lifecycle.producer import LifecycleProducer

        cls._invalidate_amsdal_state()

        class AmsdalInitConsumer(LifecycleConsumer):
            def on_event(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
                settings.override(APP_PATH=output_path)

                config_manager = AmsdalConfigManager()
                config_manager.load_config(config_path)

                amsdal_manager = AmsdalManager()
                if not amsdal_manager.is_setup:
                    amsdal_manager.setup()
                amsdal_manager.authenticate()
                amsdal_manager.init_classes()

            async def on_event_async(self, *args: Any, **kwargs: Any) -> None:
                pass

        LifecycleProducer.add_listener(
            LifecycleEvent.ON_SERVER_STARTUP,
            AmsdalInitConsumer,
            insert_first=True,
        )
        start(**kwargs)

    @classmethod
    def _build_models_and_migrate(
        cls,
        queue: QueueType,
        cli_config: CliConfig,
        app_source_path: Path,
        output_path: Path,
        config_path: Path,
        *,
        apply_fixtures: bool,
    ) -> None:
        queue.put(STOP_SERVER_EVENT)
        cls._invalidate_amsdal_state()
        amsdal_manager = build_app_and_check_migrations(
            cli_config=cli_config,
            output_path=output_path,
            app_source_path=app_source_path,
            config_path=config_path,
            apply_fixtures=apply_fixtures,
        )

        amsdal_manager.teardown()

        queue.put(START_SERVER_EVENT)

    @staticmethod
    def _invalidate_amsdal_state() -> None:
        try:
            amsdal_manager = AmsdalManager()
            amsdal_manager.teardown()
        except AmsdalRuntimeError:
            ...

        AmsdalManager.invalidate()
        ClassManager.invalidate()
        ClassVersionManager.invalidate()

    @staticmethod
    def _build_static_files(
        cli_config: CliConfig,
        app_source_path: Path,
        output_path: Path,
        config_path: Path,
    ) -> None:
        builder = AppBuilder(
            cli_config=cli_config,
            config_path=config_path,
        )
        builder.pre_build(output_path)

        rprint(rich_info('Building static files...'), end=' ')
        builder.build_static_files(app_source_path)
        rprint(rich_success('OK!'))

    @staticmethod
    def _build_transactions(
        cli_config: CliConfig,
        app_source_path: Path,
        output_path: Path,
        config_path: Path,
    ) -> None:
        builder = AppBuilder(
            cli_config=cli_config,
            config_path=config_path,
        )
        builder.pre_build(output_path)

        rprint(rich_info('Building transactions...'), end=' ')
        builder.build_transactions(app_source_path)
        rprint(rich_success('OK!'))

    @staticmethod
    def _watch(
        name: str,
        path: Path,
        *other_args: Any,
        target: str | Callable[..., Any],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        **other_kwargs: Any,
    ) -> None:
        try:
            if not path.exists():
                process = spawn_context.Process(
                    target=target,  # type: ignore[arg-type]
                    args=args,
                    kwargs=kwargs,  # type: ignore[arg-type]
                )
                process.start()
                process.join()

                while not path.exists():
                    sleep(3)

            run_process(path, *other_args, target=target, args=args, kwargs=kwargs, **other_kwargs)
        except KeyboardInterrupt:
            rprint(f'[yellow]Task {name} was gracefully stopped[/yellow]')
