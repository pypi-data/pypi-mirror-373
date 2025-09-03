from enum import Enum


class CollectionAuthorizationSetIdentityAction(str, Enum):
    SET_IDENTITY = "set-identity"

    def __str__(self) -> str:
        return str(self.value)
