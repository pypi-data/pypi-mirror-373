from enum import Enum


class CollectionsItemsCreateItemJsonNewItemRequestContentType1(str, Enum):
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
