from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from amsdal.manager import AmsdalManager
from amsdal.utils.tests.enums import DbExecutionType
from amsdal.utils.tests.enums import LakehouseOption
from amsdal.utils.tests.enums import StateOption
from amsdal.utils.tests.helpers import init_manager_and_migrate

SRC_DIR = Path(__file__).parent.parent


def pytest_addoption(parser: Any) -> None:
    parser.addoption('--db_execution_type', action='store', default=DbExecutionType.include_state_db)
    parser.addoption('--state_option', action='store', default=StateOption.sqlite)
    parser.addoption('--lakehouse_option', action='store', default=LakehouseOption.sqlite)


@pytest.fixture(scope='module')
def lakehouse_option(request: Any) -> str:
    return request.config.getoption('--lakehouse_option')


@pytest.fixture(scope='module')
def db_execution_type(request: Any) -> str:
    return request.config.getoption('--db_execution_type')


@pytest.fixture(scope='module')
def state_option(request: Any) -> str:
    return request.config.getoption('--state_option')


@pytest.fixture(scope='function', autouse=True)
def init_db(
    db_execution_type: DbExecutionType,
    state_option: StateOption,
    lakehouse_option: LakehouseOption,
) -> Generator[AmsdalManager, Any, None]:
    with init_manager_and_migrate(
        src_dir_path=SRC_DIR,
        db_execution_type=db_execution_type,
        lakehouse_option=lakehouse_option,
        state_option=state_option,
    ) as manager:
        yield manager
