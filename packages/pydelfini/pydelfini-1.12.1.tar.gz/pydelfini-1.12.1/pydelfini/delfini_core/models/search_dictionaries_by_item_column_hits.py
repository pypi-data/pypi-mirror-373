from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.column_schema_type import ColumnSchemaType
from ..models.search_dictionaries_by_item_column_hits_search_dictionaries_hit import (
    SearchDictionariesByItemColumnHitsSearchDictionariesHit,
)


T = TypeVar("T", bound="SearchDictionariesByItemColumnHits")


@_attrs_define
class SearchDictionariesByItemColumnHits:
    """SearchDictionariesByItemColumnHits model

    Attributes:
        hits (List['SearchDictionariesByItemColumnHitsSearchDictionariesHit']):
        name (str):
        type_as_parsed (ColumnSchemaType):
    """

    hits: List["SearchDictionariesByItemColumnHitsSearchDictionariesHit"]
    name: str
    type_as_parsed: ColumnSchemaType

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        hits = []
        for hits_item_data in self.hits:
            hits_item = hits_item_data.to_dict()
            hits.append(hits_item)

        name = self.name
        type_as_parsed = self.type_as_parsed.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "hits": hits,
                "name": name,
                "type_as_parsed": type_as_parsed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchDictionariesByItemColumnHits` from a dict"""
        d = src_dict.copy()
        hits = []
        _hits = d.pop("hits")
        for hits_item_data in _hits:
            hits_item = (
                SearchDictionariesByItemColumnHitsSearchDictionariesHit.from_dict(
                    hits_item_data
                )
            )

            hits.append(hits_item)

        name = d.pop("name")

        type_as_parsed = ColumnSchemaType(d.pop("type_as_parsed"))

        search_dictionaries_by_item_column_hits = cls(
            hits=hits,
            name=name,
            type_as_parsed=type_as_parsed,
        )

        return search_dictionaries_by_item_column_hits
