import json
from pathlib import Path

from amsdal_cli.commands.api_check.operation_log import OperationLog


def load_operation_logs(logs_path: Path) -> list[OperationLog]:
    data_str = logs_path.read_text()
    data_raw = json.loads(data_str)

    return [OperationLog(**item) for item in data_raw]
