from enum import Enum


class CollectionAuthorizationRemoveIdentityAction(str, Enum):
    REMOVE_IDENTITY = "remove-identity"

    def __str__(self) -> str:
        return str(self.value)
