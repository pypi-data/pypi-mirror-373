from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.bundle import Bundle
from ..models.pagination import Pagination


T = TypeVar("T", bound="CollectionsDictionariesListBundlesResponse200")


@_attrs_define
class CollectionsDictionariesListBundlesResponse200:
    """CollectionsDictionariesListBundlesResponse200 model

    Attributes:
        bundles (List['Bundle']):
        pagination (Pagination):
    """

    bundles: List["Bundle"]
    pagination: "Pagination"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        bundles = []
        for bundles_item_data in self.bundles:
            bundles_item = bundles_item_data.to_dict()
            bundles.append(bundles_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "bundles": bundles,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsDictionariesListBundlesResponse200` from a dict"""
        d = src_dict.copy()
        bundles = []
        _bundles = d.pop("bundles")
        for bundles_item_data in _bundles:
            bundles_item = Bundle.from_dict(bundles_item_data)

            bundles.append(bundles_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        collections_dictionaries_list_bundles_response_200 = cls(
            bundles=bundles,
            pagination=pagination,
        )

        return collections_dictionaries_list_bundles_response_200
