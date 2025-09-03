from enum import Enum


class ItemStatusValue(str, Enum):
    FAILED = "failed"
    NOT_APPLICABLE = "not-applicable"
    OK = "ok"
    PENDING = "pending"
    SERVER_ERROR = "server-error"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
