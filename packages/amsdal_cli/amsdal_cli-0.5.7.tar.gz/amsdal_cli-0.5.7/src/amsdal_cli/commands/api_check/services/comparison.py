import difflib

from rich import print as rprint

from amsdal_cli.commands.api_check.operation_log import OperationLog
from amsdal_cli.utils.text import rich_error
from amsdal_cli.utils.text import rich_success


def compare(
    target_logs: list[OperationLog],
    compare_logs: list[OperationLog],
) -> tuple[list[tuple[OperationLog, OperationLog]], bool]:
    diffs: list[tuple[OperationLog, OperationLog]] = []
    error: bool = False
    for idx, log in enumerate(target_logs):
        if idx >= len(compare_logs):
            rprint(rich_error(f'Not found: {len(target_logs[idx:])}, rest logs: {target_logs[idx:]}'))
            error = True
            break

        if log.id != compare_logs[idx].id:
            rprint(rich_error(f'Log {log.id} != {compare_logs[idx].id}'))
            error = True
            break

        if log != compare_logs[idx]:
            diffs.append((log, compare_logs[idx]))
    return diffs, error


def check(target_logs: list[OperationLog], compare_logs: list[OperationLog]) -> bool:
    diffs, error = compare(target_logs, compare_logs)
    if not diffs and not error:
        rprint(rich_success('No differences found!'))
        return False

    differ = difflib.Differ()

    rprint(rich_error('Differences found:'))
    for log, compare_log in diffs:
        str1 = str(log)
        str2 = str(compare_log)
        diff = list(differ.compare(str1.splitlines(), str2.splitlines()))
        rprint(rich_error('\n'.join(diff)))

    return True
