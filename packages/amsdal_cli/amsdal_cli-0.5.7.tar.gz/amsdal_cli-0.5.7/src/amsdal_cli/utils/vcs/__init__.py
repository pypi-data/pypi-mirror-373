from typing import TYPE_CHECKING

from amsdal_cli.utils.vcs.base import VCSBaseService
from amsdal_cli.utils.vcs.dummy import DummyVSCService
from amsdal_cli.utils.vcs.enums import VCSOptions
from amsdal_cli.utils.vcs.git import GitService

if TYPE_CHECKING:
    from amsdal_cli.utils.cli_config import CliConfig


def get_vcs_service(config: 'CliConfig') -> VCSBaseService:
    if config.vcs == VCSOptions.git:
        return GitService(config)
    return DummyVSCService(config)


__all__ = ['get_vcs_service']
