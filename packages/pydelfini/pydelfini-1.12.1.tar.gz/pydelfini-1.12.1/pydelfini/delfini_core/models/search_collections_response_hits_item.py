from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.collection import Collection
from ..models.highlights import Highlights
from ..models.search_collections_response_hits_item_data_elements_item import (
    SearchCollectionsResponseHitsItemDataElementsItem,
)
from ..models.search_collections_response_hits_item_items_item import (
    SearchCollectionsResponseHitsItemItemsItem,
)


T = TypeVar("T", bound="SearchCollectionsResponseHitsItem")


@_attrs_define
class SearchCollectionsResponseHitsItem:
    """SearchCollectionsResponseHitsItem model

    Attributes:
        collection (Collection): Core collection properties, with IDs
        data_elements (List['SearchCollectionsResponseHitsItemDataElementsItem']):
        highlights (Highlights):
        items (List['SearchCollectionsResponseHitsItemItemsItem']):
        score (float):
    """

    collection: "Collection"
    data_elements: List["SearchCollectionsResponseHitsItemDataElementsItem"]
    highlights: "Highlights"
    items: List["SearchCollectionsResponseHitsItemItemsItem"]
    score: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        collection = self.collection.to_dict()
        data_elements = []
        for data_elements_item_data in self.data_elements:
            data_elements_item = data_elements_item_data.to_dict()
            data_elements.append(data_elements_item)

        highlights = self.highlights.to_dict()
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        score = self.score

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "collection": collection,
                "dataElements": data_elements,
                "highlights": highlights,
                "items": items,
                "score": score,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchCollectionsResponseHitsItem` from a dict"""
        d = src_dict.copy()
        collection = Collection.from_dict(d.pop("collection"))

        data_elements = []
        _data_elements = d.pop("dataElements")
        for data_elements_item_data in _data_elements:
            data_elements_item = (
                SearchCollectionsResponseHitsItemDataElementsItem.from_dict(
                    data_elements_item_data
                )
            )

            data_elements.append(data_elements_item)

        highlights = Highlights.from_dict(d.pop("highlights"))

        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = SearchCollectionsResponseHitsItemItemsItem.from_dict(
                items_item_data
            )

            items.append(items_item)

        score = d.pop("score")

        search_collections_response_hits_item = cls(
            collection=collection,
            data_elements=data_elements,
            highlights=highlights,
            items=items,
            score=score,
        )

        return search_collections_response_hits_item
