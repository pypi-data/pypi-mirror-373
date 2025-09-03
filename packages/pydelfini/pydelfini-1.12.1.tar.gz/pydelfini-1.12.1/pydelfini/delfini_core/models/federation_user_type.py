from enum import Enum


class FederationUserType(str, Enum):
    PERSON = "Person"

    def __str__(self) -> str:
        return str(self.value)
