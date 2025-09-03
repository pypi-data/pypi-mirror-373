from enum import Enum


class MetadataFieldGroupResource(str, Enum):
    ACCOUNT = "account"
    COLLECTION = "collection"
    COLLECTION_ITEM = "collection-item"
    GROUP = "group"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
