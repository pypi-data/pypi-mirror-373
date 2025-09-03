from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.dictionary_search_options_options_additional_property import (
    DictionarySearchOptionsOptionsAdditionalProperty,
)


T = TypeVar("T", bound="DictionarySearchOptionsOptions")


@_attrs_define
class DictionarySearchOptionsOptions:
    """DictionarySearchOptionsOptions model"""

    additional_properties: Dict[
        str, "DictionarySearchOptionsOptionsAdditionalProperty"
    ] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DictionarySearchOptionsOptions` from a dict"""
        d = src_dict.copy()
        dictionary_search_options_options = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = (
                DictionarySearchOptionsOptionsAdditionalProperty.from_dict(prop_dict)
            )

            additional_properties[prop_name] = additional_property

        dictionary_search_options_options.additional_properties = additional_properties
        return dictionary_search_options_options

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(
        self, key: str
    ) -> "DictionarySearchOptionsOptionsAdditionalProperty":
        return self.additional_properties[key]

    def __setitem__(
        self, key: str, value: "DictionarySearchOptionsOptionsAdditionalProperty"
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
