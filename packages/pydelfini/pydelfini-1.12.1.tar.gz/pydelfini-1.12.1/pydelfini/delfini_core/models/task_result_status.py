from enum import Enum


class TaskResultStatus(str, Enum):
    CANCELED = "CANCELED"
    CANCELED_FAILED = "CANCELED_FAILED"
    CANCELED_PAST_DEADLINE = "CANCELED_PAST_DEADLINE"
    FAILED = "FAILED"
    FAILED_RETRY = "FAILED_RETRY"
    OK = "OK"
    TIMEOUT_CANCELED = "TIMEOUT_CANCELED"
    TIMEOUT_FAILED = "TIMEOUT_FAILED"
    TIMEOUT_RETRY = "TIMEOUT_RETRY"

    def __str__(self) -> str:
        return str(self.value)
