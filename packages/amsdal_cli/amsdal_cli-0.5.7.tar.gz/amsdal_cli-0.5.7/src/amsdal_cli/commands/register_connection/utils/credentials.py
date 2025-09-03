from contextlib import suppress
from pathlib import Path
from typing import Any


def process_credentials(credentials: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {}

    cast_type: type[str | Path]
    for credential in credentials:
        key, value = credential.split('=', 1)
        cast_type = str

        if value.endswith('::path'):
            value = value[:-6]
            cast_type = Path

        if value.startswith('"') or value.startswith("'"):
            value = value[1:-1]
        else:
            with suppress(ValueError):
                _val = float(value)

                if str(_val) == value:
                    data[key] = _val
                    continue

            with suppress(ValueError):
                _val = int(value)

                if str(_val) == value:
                    data[key] = _val
                    continue

            if value.lower() in ('true', 'false'):
                data[key] = value.lower() == 'true'
                continue

        data[key] = cast_type(value)

    return data
