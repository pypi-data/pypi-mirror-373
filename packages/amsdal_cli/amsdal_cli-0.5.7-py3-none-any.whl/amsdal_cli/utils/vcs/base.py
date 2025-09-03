from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amsdal_cli.utils.cli_config import CliConfig


class VCSBaseService(ABC):
    def __init__(self, config: 'CliConfig') -> None:
        self.config = config

    @abstractmethod
    def get_current_branch(self) -> str:
        pass

    @abstractmethod
    def checkout(self, branch: str) -> None:
        pass
