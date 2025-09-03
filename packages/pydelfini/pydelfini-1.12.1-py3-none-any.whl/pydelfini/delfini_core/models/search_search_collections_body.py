from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.search_search_collections_body_types_item import (
    SearchSearchCollectionsBodyTypesItem,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SearchSearchCollectionsBody")


@_attrs_define
class SearchSearchCollectionsBody:
    """SearchSearchCollectionsBody model

    Attributes:
        query (str):
        bmeta (Union[Unset, str]): Filter by collection metadata.

            Provide a base64-encoded JSON mapping conformant to the
            following JSON schema:

              schema:
                type: object
                additionalProperties:
                  anyOf:
                    - type: string
                    - type: array
                      items:
                        type: string

            This includes any combination of `{"x-meta": "foo"}` and
            `{"x-meta-2": ["foo", "bar"]}`:

            * In the single string case, the provided string must
              match exactly to the value in the metadata field.

            * In the case of an array of strings, the metadata field
              is assumed to contain a JSON-encoded array of strings,
              and only one of the strings in the provided array needs
              to match one of the strings in the metadata field.
        data_elements (Union[Unset, List[str]]):
        types (Union[Unset, List[SearchSearchCollectionsBodyTypesItem]]):
    """

    query: str
    bmeta: Union[Unset, str] = UNSET
    data_elements: Union[Unset, List[str]] = UNSET
    types: Union[Unset, List[SearchSearchCollectionsBodyTypesItem]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        query = self.query
        bmeta = self.bmeta
        data_elements: Union[Unset, List[str]] = UNSET
        if not isinstance(self.data_elements, Unset):
            data_elements = self.data_elements

        types: Union[Unset, List[str]] = UNSET
        if not isinstance(self.types, Unset):
            types = []
            for types_item_data in self.types:
                types_item = types_item_data.value
                types.append(types_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "query": query,
            }
        )
        if bmeta is not UNSET:
            field_dict["bmeta"] = bmeta
        if data_elements is not UNSET:
            field_dict["data_elements"] = data_elements
        if types is not UNSET:
            field_dict["types"] = types

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchSearchCollectionsBody` from a dict"""
        d = src_dict.copy()
        query = d.pop("query")

        bmeta = d.pop("bmeta", UNSET)

        data_elements = cast(List[str], d.pop("data_elements", UNSET))

        types = []
        _types = d.pop("types", UNSET)
        for types_item_data in _types or []:
            types_item = SearchSearchCollectionsBodyTypesItem(types_item_data)

            types.append(types_item)

        search_search_collections_body = cls(
            query=query,
            bmeta=bmeta,
            data_elements=data_elements,
            types=types,
        )

        return search_search_collections_body
