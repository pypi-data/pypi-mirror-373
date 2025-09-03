from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.search_dictionaries_inverse_result import SearchDictionariesInverseResult


T = TypeVar("T", bound="SearchDictionariesByItemInverseResponse")


@_attrs_define
class SearchDictionariesByItemInverseResponse:
    """SearchDictionariesByItemInverseResponse model

    Attributes:
        results (List['SearchDictionariesInverseResult']):
    """

    results: List["SearchDictionariesInverseResult"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "results": results,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchDictionariesByItemInverseResponse` from a dict"""
        d = src_dict.copy()
        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = SearchDictionariesInverseResult.from_dict(results_item_data)

            results.append(results_item)

        search_dictionaries_by_item_inverse_response = cls(
            results=results,
        )

        return search_dictionaries_by_item_inverse_response
