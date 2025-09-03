from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.search_search_accounts_body_types_item import (
    SearchSearchAccountsBodyTypesItem,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SearchSearchAccountsBody")


@_attrs_define
class SearchSearchAccountsBody:
    """SearchSearchAccountsBody model

    Attributes:
        query (str):
        account_bmeta (Union[Unset, str]): Filter by account metadata.

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
        types (Union[Unset, List[SearchSearchAccountsBodyTypesItem]]):
    """

    query: str
    account_bmeta: Union[Unset, str] = UNSET
    types: Union[Unset, List[SearchSearchAccountsBodyTypesItem]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        query = self.query
        account_bmeta = self.account_bmeta
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
        if account_bmeta is not UNSET:
            field_dict["accountBmeta"] = account_bmeta
        if types is not UNSET:
            field_dict["types"] = types

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchSearchAccountsBody` from a dict"""
        d = src_dict.copy()
        query = d.pop("query")

        account_bmeta = d.pop("accountBmeta", UNSET)

        types = []
        _types = d.pop("types", UNSET)
        for types_item_data in _types or []:
            types_item = SearchSearchAccountsBodyTypesItem(types_item_data)

            types.append(types_item)

        search_search_accounts_body = cls(
            query=query,
            account_bmeta=account_bmeta,
            types=types,
        )

        return search_search_accounts_body
