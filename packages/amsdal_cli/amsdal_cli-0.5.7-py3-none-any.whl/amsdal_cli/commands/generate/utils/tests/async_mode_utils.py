import ast
from typing import TypeVar

from amsdal_utils.config.manager import AmsdalConfigManager

AwaitExprT = TypeVar('AwaitExprT', bound=ast.expr)


def maybe_await(value: AwaitExprT) -> AwaitExprT | ast.Await:
    return ast.Await(value=value) if AmsdalConfigManager().get_config().async_mode else value
