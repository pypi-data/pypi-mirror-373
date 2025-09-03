from enum import Enum


class MetadataMetricType(str, Enum):
    METADATA = "metadata"

    def __str__(self) -> str:
        return str(self.value)
