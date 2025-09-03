from enum import Enum


class CollectionAccessLevel(str, Enum):
    CONFIDENTIAL = "confidential"
    CONTROLLED = "controlled"
    PRIVATE = "private"
    PUBLIC = "public"

    def __str__(self) -> str:
        return str(self.value)
