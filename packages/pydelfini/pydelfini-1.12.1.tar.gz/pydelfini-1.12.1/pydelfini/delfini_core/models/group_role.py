from enum import Enum


class GroupRole(str, Enum):
    ADMIN = "ADMIN"
    AUTHOR = "AUTHOR"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

    def __str__(self) -> str:
        return str(self.value)
