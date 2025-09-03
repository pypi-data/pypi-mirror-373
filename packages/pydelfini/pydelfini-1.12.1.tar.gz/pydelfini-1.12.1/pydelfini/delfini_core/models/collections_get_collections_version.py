from enum import Enum


class CollectionsGetCollectionsVersion(str, Enum):
    ALL = "all"
    LATEST = "latest"
    LIVE = "live"

    def __str__(self) -> str:
        return str(self.value)
