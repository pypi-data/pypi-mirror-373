from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.collection import Collection
from ..models.pagination import Pagination


T = TypeVar("T", bound="CollectionsGetCollectionsCollectionList")


@_attrs_define
class CollectionsGetCollectionsCollectionList:
    """CollectionsGetCollectionsCollectionList model

    Attributes:
        collections (List['Collection']):
        pagination (Pagination):
    """

    collections: List["Collection"]
    pagination: "Pagination"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        collections = []
        for collections_item_data in self.collections:
            collections_item = collections_item_data.to_dict()
            collections.append(collections_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "collections": collections,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsGetCollectionsCollectionList` from a dict"""
        d = src_dict.copy()
        collections = []
        _collections = d.pop("collections")
        for collections_item_data in _collections:
            collections_item = Collection.from_dict(collections_item_data)

            collections.append(collections_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        collections_get_collections_collection_list = cls(
            collections=collections,
            pagination=pagination,
        )

        return collections_get_collections_collection_list
