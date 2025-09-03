from watchfiles.filters import DefaultFilter


class ModelsWatchFilter(DefaultFilter):
    def __init__(self) -> None:
        super().__init__(ignore_dirs=['fixtures'])
