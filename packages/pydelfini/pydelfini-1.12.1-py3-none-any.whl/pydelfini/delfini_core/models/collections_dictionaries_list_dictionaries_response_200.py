from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_dictionary import DataDictionary
from ..models.pagination import Pagination


T = TypeVar("T", bound="CollectionsDictionariesListDictionariesResponse200")


@_attrs_define
class CollectionsDictionariesListDictionariesResponse200:
    """CollectionsDictionariesListDictionariesResponse200 model

    Attributes:
        dictionaries (List['DataDictionary']):
        pagination (Pagination):
    """

    dictionaries: List["DataDictionary"]
    pagination: "Pagination"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        dictionaries = []
        for dictionaries_item_data in self.dictionaries:
            dictionaries_item = dictionaries_item_data.to_dict()
            dictionaries.append(dictionaries_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dictionaries": dictionaries,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsDictionariesListDictionariesResponse200` from a dict"""
        d = src_dict.copy()
        dictionaries = []
        _dictionaries = d.pop("dictionaries")
        for dictionaries_item_data in _dictionaries:
            dictionaries_item = DataDictionary.from_dict(dictionaries_item_data)

            dictionaries.append(dictionaries_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        collections_dictionaries_list_dictionaries_response_200 = cls(
            dictionaries=dictionaries,
            pagination=pagination,
        )

        return collections_dictionaries_list_dictionaries_response_200
