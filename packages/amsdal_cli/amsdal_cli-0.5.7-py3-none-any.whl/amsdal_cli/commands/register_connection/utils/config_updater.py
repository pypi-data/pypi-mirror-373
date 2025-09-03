import hashlib
import json
from json import JSONEncoder
from pathlib import Path
from typing import Any

import yaml

from amsdal_cli.commands.cloud.enums import DBType


class CredentialJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Path):
            return str(o.absolute())
        return super().default(o)


class ConfigUpdater:
    def __init__(self, config_path: Path) -> None:
        self._has_changes = False
        self._config_path = config_path

        with config_path.open('r') as f:
            self.config = yaml.safe_load(f)

    def __enter__(self) -> 'ConfigUpdater':
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is None and self._has_changes:
            self.save()

    def save(self) -> None:
        with self._config_path.open('w') as f:
            yaml.safe_dump(self.config, f)

    def add_connection(
        self,
        db_type: DBType,
        connection_name: str | None,
        backend: str | None,
        credentials: dict[str, Any],
    ) -> tuple[str, bool]:
        _connection_name = self._resolve_connection_name(connection_name, credentials)
        _backend = self._resolve_backend(db_type, backend)
        existing_connections = self.config.get('connections', [])
        connection_exists = any(conn.get('name') == _connection_name for conn in existing_connections)

        if connection_exists:
            return _connection_name, False

        _credentials = [
            {key: str(val.absolute()) if isinstance(val, Path) else val} for key, val in credentials.items()
        ]

        existing_connections.append(
            {
                'name': _connection_name,
                'backend': _backend,
                'credentials': _credentials,
            }
        )

        self._has_changes = True
        return _connection_name, True

    def link_connection_to_models(self, connection_name: str, models: list[str]) -> None:
        _existing_models = self.config['resources_config']['repository'].setdefault('models', {})
        _existing_models.update(dict.fromkeys(models, connection_name))
        self._has_changes = True

    def _resolve_connection_name(self, name: str | None, credentials: dict[str, Any]) -> str:
        if name is not None:
            return name

        # try to resolve connection name from the credentials
        _credentials_sha256_hex = hashlib.sha256(
            json.dumps(credentials, cls=CredentialJSONEncoder, sort_keys=True).encode(),
        ).hexdigest()
        _existing_connections = self.config.get('connections', [])
        _used_names = []

        for conn in _existing_connections:
            _used_names.append(conn['name'])
            _conn_credentials = conn.get('credentials', [])
            _conn_credentials_dict = {k: v for d in _conn_credentials for k, v in d.items()}
            _conn_credentials_sha256_hex = hashlib.sha256(
                json.dumps(_conn_credentials_dict, sort_keys=True).encode(),
            ).hexdigest()

            if _conn_credentials_sha256_hex == _credentials_sha256_hex:
                return conn['name']

        _conn_index = len(_used_names)

        while True:
            _conn_index += 1
            _name = f'conn_{_conn_index}'

            if _name not in _used_names:
                return _name

    def _resolve_backend(
        self,
        db_type: DBType,
        backend: str | None,
    ) -> str:
        from amsdal_data.aliases.db import POSTGRES_STATE_ALIAS
        from amsdal_data.aliases.db import POSTGRES_STATE_ASYNC_ALIAS
        from amsdal_data.aliases.db import SQLITE_ALIAS
        from amsdal_data.aliases.db import SQLITE_ASYNC_ALIAS

        is_async = self.config.get('async_mode', False)

        if backend is not None:
            return backend

        if db_type == DBType.postgres:
            return POSTGRES_STATE_ASYNC_ALIAS if is_async else POSTGRES_STATE_ALIAS

        if db_type == DBType.csv:
            return 'amsdal_glue_connections.sql.connections.csv_connection.sync_connection.CsvConnection'

        return SQLITE_ASYNC_ALIAS if is_async else SQLITE_ALIAS
