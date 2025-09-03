from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.dictionary_search_options import DictionarySearchOptions


T = TypeVar("T", bound="SearchGetDictionarySearchOptionsResponse200")


@_attrs_define
class SearchGetDictionarySearchOptionsResponse200:
    """SearchGetDictionarySearchOptionsResponse200 model

    Attributes:
        sources (List['DictionarySearchOptions']):
    """

    sources: List["DictionarySearchOptions"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "sources": sources,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchGetDictionarySearchOptionsResponse200` from a dict"""
        d = src_dict.copy()
        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = DictionarySearchOptions.from_dict(sources_item_data)

            sources.append(sources_item)

        search_get_dictionary_search_options_response_200 = cls(
            sources=sources,
        )

        return search_get_dictionary_search_options_response_200
