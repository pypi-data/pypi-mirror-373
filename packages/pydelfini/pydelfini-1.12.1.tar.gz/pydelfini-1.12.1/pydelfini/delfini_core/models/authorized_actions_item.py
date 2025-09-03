from enum import Enum


class AuthorizedActionsItem(str, Enum):
    CREATE = "Create"
    DELETE = "Delete"
    GET = "Get"
    GRANT = "Grant"
    UPDATE = "Update"
    VIEW = "View"

    def __str__(self) -> str:
        return str(self.value)
