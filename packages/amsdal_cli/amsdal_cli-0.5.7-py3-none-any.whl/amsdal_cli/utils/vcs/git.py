from typing import TYPE_CHECKING

from git.exc import GitCommandError
from git.repo.base import Repo
from rich import print as rprint

from amsdal_cli.utils.text import rich_error
from amsdal_cli.utils.text import rich_highlight
from amsdal_cli.utils.text import rich_info
from amsdal_cli.utils.vcs.base import VCSBaseService

if TYPE_CHECKING:
    from amsdal_cli.utils.cli_config import CliConfig


class GitService(VCSBaseService):
    def __init__(self, config: 'CliConfig') -> None:
        super().__init__(config)
        self.repo = Repo(self.config.app_directory)

    def get_current_branch(self) -> str:
        return self.repo.active_branch.name

    def checkout(self, branch: str) -> None:
        try:
            try:
                self.repo.git.checkout(branch)
                rprint(rich_info(f'[GIT] Branch {rich_highlight(branch)} checked out'))
            except GitCommandError as e:
                if 'did not match' not in str(e):
                    raise

                self.repo.git.checkout('-b', branch)
                rprint(rich_info(f'[GIT] Branch {rich_highlight(branch)} created and checked out'))
        except Exception as e:
            rprint(rich_error(f'[GIT] Failed to checkout branch {rich_highlight(branch)}: {e}'))
