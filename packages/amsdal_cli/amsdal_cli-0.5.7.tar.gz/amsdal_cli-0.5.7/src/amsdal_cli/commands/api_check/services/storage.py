import json
from pathlib import Path

from amsdal_cli.commands.api_check.operation_log import BytesJSONEncoder
from amsdal_cli.commands.api_check.operation_log import OperationLog


def save(logs: list[OperationLog], destination: Path) -> None:
    destination.parent.mkdir(exist_ok=True, parents=True)
    # Convert OperationLog objects to dictionaries before serialization
    serializable_logs = [log.model_dump() for log in logs]
    destination.write_text(json.dumps(serializable_logs, cls=BytesJSONEncoder))
