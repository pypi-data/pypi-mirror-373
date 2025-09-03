from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_element import DataElement
from ..models.search_dictionaries_inverse_result_queries_item import (
    SearchDictionariesInverseResultQueriesItem,
)


T = TypeVar("T", bound="SearchDictionariesInverseResult")


@_attrs_define
class SearchDictionariesInverseResult:
    """SearchDictionariesInverseResult model

    Attributes:
        element (DataElement): Delfini Data Element
        queries (List['SearchDictionariesInverseResultQueriesItem']):
    """

    element: "DataElement"
    queries: List["SearchDictionariesInverseResultQueriesItem"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        element = self.element.to_dict()
        queries = []
        for queries_item_data in self.queries:
            queries_item = queries_item_data.to_dict()
            queries.append(queries_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "element": element,
                "queries": queries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchDictionariesInverseResult` from a dict"""
        d = src_dict.copy()
        element = DataElement.from_dict(d.pop("element"))

        queries = []
        _queries = d.pop("queries")
        for queries_item_data in _queries:
            queries_item = SearchDictionariesInverseResultQueriesItem.from_dict(
                queries_item_data
            )

            queries.append(queries_item)

        search_dictionaries_inverse_result = cls(
            element=element,
            queries=queries,
        )

        return search_dictionaries_inverse_result
