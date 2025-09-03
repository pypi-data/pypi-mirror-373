from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.search_search_dictionaries_body_options import (
    SearchSearchDictionariesBodyOptions,
)


T = TypeVar("T", bound="SearchSearchDictionariesBody")


@_attrs_define
class SearchSearchDictionariesBody:
    """SearchSearchDictionariesBody model

    Attributes:
        options (SearchSearchDictionariesBodyOptions):
        query (str):
        source (str):
    """

    options: "SearchSearchDictionariesBodyOptions"
    query: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        options = self.options.to_dict()
        query = self.query
        source = self.source

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "options": options,
                "query": query,
                "source": source,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchSearchDictionariesBody` from a dict"""
        d = src_dict.copy()
        options = SearchSearchDictionariesBodyOptions.from_dict(d.pop("options"))

        query = d.pop("query")

        source = d.pop("source")

        search_search_dictionaries_body = cls(
            options=options,
            query=query,
            source=source,
        )

        return search_search_dictionaries_body
