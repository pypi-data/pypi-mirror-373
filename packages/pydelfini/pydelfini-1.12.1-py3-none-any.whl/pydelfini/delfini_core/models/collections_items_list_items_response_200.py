from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.item import Item
from ..models.pagination import Pagination


T = TypeVar("T", bound="CollectionsItemsListItemsResponse200")


@_attrs_define
class CollectionsItemsListItemsResponse200:
    """CollectionsItemsListItemsResponse200 model

    Attributes:
        items (List['Item']):
        pagination (Pagination):
    """

    items: List["Item"]
    pagination: "Pagination"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "items": items,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsItemsListItemsResponse200` from a dict"""
        d = src_dict.copy()
        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = Item.from_dict(items_item_data)

            items.append(items_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        collections_items_list_items_response_200 = cls(
            items=items,
            pagination=pagination,
        )

        return collections_items_list_items_response_200
