from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.search_search_dictionaries_by_item_body_method import (
    SearchSearchDictionariesByItemBodyMethod,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SearchSearchDictionariesByItemBody")


@_attrs_define
class SearchSearchDictionariesByItemBody:
    """SearchSearchDictionariesByItemBody model

    Attributes:
        collection_id (str):
        item_id (str):
        source (str):
        version_id (str):
        method (Union[Unset, SearchSearchDictionariesByItemBodyMethod]):
    """

    collection_id: str
    item_id: str
    source: str
    version_id: str
    method: Union[Unset, SearchSearchDictionariesByItemBodyMethod] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        collection_id = self.collection_id
        item_id = self.item_id
        source = self.source
        version_id = self.version_id
        method: Union[Unset, str] = UNSET
        if not isinstance(self.method, Unset):
            method = self.method.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "collection_id": collection_id,
                "item_id": item_id,
                "source": source,
                "version_id": version_id,
            }
        )
        if method is not UNSET:
            field_dict["method"] = method

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchSearchDictionariesByItemBody` from a dict"""
        d = src_dict.copy()
        collection_id = d.pop("collection_id")

        item_id = d.pop("item_id")

        source = d.pop("source")

        version_id = d.pop("version_id")

        _method = d.pop("method", UNSET)
        method: Union[Unset, SearchSearchDictionariesByItemBodyMethod]
        if isinstance(_method, Unset):
            method = UNSET
        else:
            method = SearchSearchDictionariesByItemBodyMethod(_method)

        search_search_dictionaries_by_item_body = cls(
            collection_id=collection_id,
            item_id=item_id,
            source=source,
            version_id=version_id,
            method=method,
        )

        return search_search_dictionaries_by_item_body
