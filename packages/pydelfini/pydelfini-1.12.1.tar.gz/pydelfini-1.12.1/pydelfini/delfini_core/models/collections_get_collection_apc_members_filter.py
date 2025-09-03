from enum import Enum


class CollectionsGetCollectionApcMembersFilter(str, Enum):
    MYSELF = "myself"
    OWNERS = "owners"

    def __str__(self) -> str:
        return str(self.value)
