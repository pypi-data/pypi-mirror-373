from collections import defaultdict
from collections.abc import Callable
from typing import TYPE_CHECKING

from rich import print as rprint

if TYPE_CHECKING:
    from amsdal_models.migration.data_classes import MigrationFile


def render_migrations_list(
    migrations: list['MigrationFile'],
    color: str | Callable[['MigrationFile'], str] = 'yellow',
    *,
    is_migrated: bool | Callable[['MigrationFile'], bool] = False,
) -> None:
    from amsdal_utils.models.enums import ModuleType

    from amsdal_cli.utils.text import rich_success

    migrations_per_type = defaultdict(list)

    for migration in migrations:
        migrations_per_type[migration.type].append(migration)

    if ModuleType.CORE in migrations_per_type:
        rprint(rich_success('Core:'))

        for migration in migrations_per_type[ModuleType.CORE]:
            if callable(color):
                _color = color(migration)
            else:
                _color = color

            if callable(is_migrated):
                _is_migrated = is_migrated(migration)
            else:
                _is_migrated = is_migrated

            rprint(rf'[{_color}]  - \[{_is_migrated_mark(is_migrated=_is_migrated)}] {migration.path.name}[/{_color}]')

    if ModuleType.CONTRIB in migrations_per_type:
        rprint(rich_success('Contrib:'))

        for migration in migrations_per_type[ModuleType.CONTRIB]:
            if migration.module:
                contrib_name = '.'.join(migration.module.split('.')[:-1])
            else:
                contrib_name = 'N/A'

            if callable(color):
                _color = color(migration)
            else:
                _color = color

            if callable(is_migrated):
                _is_migrated = is_migrated(migration)
            else:
                _is_migrated = is_migrated

            _mark = _is_migrated_mark(is_migrated=_is_migrated)
            rprint(
                rf'[{_color}]  - \[{_mark}] {contrib_name}: {migration.path.name}[/{_color}]',
            )

    if ModuleType.USER in migrations_per_type:
        rprint(rich_success('App:'))

        for migration in migrations_per_type[ModuleType.USER]:
            if callable(color):
                _color = color(migration)
            else:
                _color = color

            if callable(is_migrated):
                _is_migrated = is_migrated(migration)
            else:
                _is_migrated = is_migrated

            rprint(
                rf'[{_color}]  - \[{_is_migrated_mark(is_migrated=_is_migrated)}] {migration.path.name}[/{_color}]',
            )


def _is_migrated_mark(*, is_migrated: bool) -> str:
    return 'x' if is_migrated else ' '
