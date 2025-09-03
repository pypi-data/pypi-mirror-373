from enum import Enum


class EventMetricType(str, Enum):
    EVENT = "event"

    def __str__(self) -> str:
        return str(self.value)
