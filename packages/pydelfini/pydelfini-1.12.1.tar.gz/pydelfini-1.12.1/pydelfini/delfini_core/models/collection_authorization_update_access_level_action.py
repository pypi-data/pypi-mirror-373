from enum import Enum


class CollectionAuthorizationUpdateAccessLevelAction(str, Enum):
    UPDATE_ACCESS_LEVEL = "update-access-level"

    def __str__(self) -> str:
        return str(self.value)
