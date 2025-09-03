from enum import Enum


class CollectionRole(str, Enum):
    ADMIN = "ADMIN"
    READER = "READER"
    VIEWER = "VIEWER"
    WRITER = "WRITER"

    def __str__(self) -> str:
        return str(self.value)
