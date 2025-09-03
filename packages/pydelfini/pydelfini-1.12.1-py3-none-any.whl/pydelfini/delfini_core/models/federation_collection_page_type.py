from enum import Enum


class FederationCollectionPageType(str, Enum):
    ORDEREDCOLLECTION = "OrderedCollection"
    ORDEREDCOLLECTIONPAGE = "OrderedCollectionPage"

    def __str__(self) -> str:
        return str(self.value)
