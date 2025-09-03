from enum import Enum


class FederationCollectionType(str, Enum):
    SERVICE = "Service"

    def __str__(self) -> str:
        return str(self.value)
