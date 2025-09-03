import ast

from amsdal_utils.config.manager import AmsdalConfigManager


def test_function_arguments() -> ast.arguments:
    return ast.arguments(
        posonlyargs=[],
        args=[],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[],
    )


def test_function_decorator_list() -> list[ast.expr]:
    if AmsdalConfigManager().get_config().async_mode:
        return [ast.Name(id='pytest.mark.asyncio', ctx=ast.Load())]
    return []
