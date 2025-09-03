from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.pagination import Pagination
from ..models.search_dictionaries_by_item_column_hits import (
    SearchDictionariesByItemColumnHits,
)


T = TypeVar("T", bound="SearchDictionariesByItemResponse")


@_attrs_define
class SearchDictionariesByItemResponse:
    """SearchDictionariesByItemResponse model

    Attributes:
        columns (List['SearchDictionariesByItemColumnHits']):
        pagination (Pagination):
    """

    columns: List["SearchDictionariesByItemColumnHits"]
    pagination: "Pagination"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        columns = []
        for columns_item_data in self.columns:
            columns_item = columns_item_data.to_dict()
            columns.append(columns_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "columns": columns,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchDictionariesByItemResponse` from a dict"""
        d = src_dict.copy()
        columns = []
        _columns = d.pop("columns")
        for columns_item_data in _columns:
            columns_item = SearchDictionariesByItemColumnHits.from_dict(
                columns_item_data
            )

            columns.append(columns_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        search_dictionaries_by_item_response = cls(
            columns=columns,
            pagination=pagination,
        )

        return search_dictionaries_by_item_response
