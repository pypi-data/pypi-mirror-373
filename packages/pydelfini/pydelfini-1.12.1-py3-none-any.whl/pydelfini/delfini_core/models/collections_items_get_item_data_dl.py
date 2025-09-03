from enum import Enum


class CollectionsItemsGetItemDataDl(str, Enum):
    ATTACHMENT = "attachment"
    INLINE = "inline"

    def __str__(self) -> str:
        return str(self.value)
