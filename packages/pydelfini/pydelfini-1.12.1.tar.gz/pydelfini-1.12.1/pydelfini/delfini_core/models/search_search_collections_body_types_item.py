from enum import Enum


class SearchSearchCollectionsBodyTypesItem(str, Enum):
    COLLECTION = "collection"
    ITEM = "item"
    ITEM_DATA_ELEMENT = "item-data-element"

    def __str__(self) -> str:
        return str(self.value)
