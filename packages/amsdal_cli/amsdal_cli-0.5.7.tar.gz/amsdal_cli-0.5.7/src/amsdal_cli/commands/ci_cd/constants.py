from enum import Enum


class Vcs(str, Enum):
    github = 'github'


GITHUB_DETAILS = """Go to repository [blue]Settings -> Secrets and variables -> Actions -> New repository secret[/blue]
and add the following secrets:
- [blue]AMSDAL_ACCESS_KEY_ID[/blue]
- [blue]AMSDAL_SECRET_ACCESS_KEY[/blue]
"""
