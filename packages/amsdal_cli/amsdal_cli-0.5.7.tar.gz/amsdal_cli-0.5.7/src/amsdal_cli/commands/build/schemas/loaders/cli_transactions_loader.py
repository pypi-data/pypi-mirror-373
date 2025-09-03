import ast
from collections.abc import Iterator
from pathlib import Path

import isort

from amsdal_cli.commands.build.schemas.loaders.base import TransactionsLoaderBase


class CliTransactionsLoader(TransactionsLoaderBase):
    """
    Loader for transaction files in CLI.

    This class is responsible for loading transaction files from a given application root directory. It extends the
    `TransactionsLoaderBase` to provide methods for iterating over transaction files.
    """

    def __init__(self, app_root: Path) -> None:
        self._transactions_path = app_root / 'transactions'

    def iter_transactions(self) -> Iterator[Path]:
        """
        Iterates over transaction files and yields their paths.

        This method checks if the transactions directory exists and is a directory. If the condition is met,
            it yields the paths to the transaction files in the directory.

        Yields:
            Iterator[Path]: An iterator over the paths to the transaction files in the transactions directory.
        """
        if self._transactions_path.exists() and self._transactions_path.is_dir():
            yield from self._transactions_path.iterdir()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}'


def _cleanup_transaction_file(source: str) -> str:
    # Parse the source into an AST
    module = ast.parse(source)

    import_strings = set()
    imports = []
    new_body = []

    for node in module.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):  # noqa: UP038
            import_source = ast.unparse(node)

            if import_source in import_strings:
                continue

            imports.append(node)
            import_strings.add(import_source)
        else:
            new_body.append(node)

    new_body.sort(key=lambda node: getattr(node, 'name', ''))

    module.body = imports + new_body
    source = ast.unparse(module)

    return isort.code(
        source,
        config=isort.Config(
            force_single_line=True,
            order_by_type=True,
            known_first_party=['amsdal_models', 'models'],
        ),
    )
