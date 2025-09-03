from amsdal_cli.utils.vcs.base import VCSBaseService


class DummyVSCService(VCSBaseService):
    def get_current_branch(self) -> str:
        from amsdal_cli.commands.cloud.environments.utils import get_current_env

        return get_current_env(self.config)

    def checkout(self, branch: str) -> None:
        from amsdal_cli.commands.cloud.environments.utils import set_current_env

        set_current_env(self.config, branch)
