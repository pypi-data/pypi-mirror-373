import os
from typing import TYPE_CHECKING

from watchfiles.filters import DefaultFilter

if TYPE_CHECKING:
    from watchfiles.main import Change


class StaticFilesWatchFilter(DefaultFilter):
    def __init__(self) -> None:
        self.static_directory_name = 'static'
        super().__init__()

    def __call__(self, change: 'Change', path: str) -> bool:
        parts = path.lstrip(os.sep).split(os.sep)

        if not any(p == self.static_directory_name for p in parts):
            return False

        return super().__call__(change, path)
