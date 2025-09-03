from enum import Enum


class CollectionsGetCollectionsSort(str, Enum):
    CREATED = "created"
    NAME = "name"
    TAGS = "tags"

    def __str__(self) -> str:
        return str(self.value)
