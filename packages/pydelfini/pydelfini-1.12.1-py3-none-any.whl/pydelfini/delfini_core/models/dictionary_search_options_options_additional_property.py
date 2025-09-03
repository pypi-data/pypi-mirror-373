from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.dictionary_search_options_options_additional_property_type import (
    DictionarySearchOptionsOptionsAdditionalPropertyType,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="DictionarySearchOptionsOptionsAdditionalProperty")


@_attrs_define
class DictionarySearchOptionsOptionsAdditionalProperty:
    """DictionarySearchOptionsOptionsAdditionalProperty model

    Attributes:
        type (DictionarySearchOptionsOptionsAdditionalPropertyType):
        default (Union[Unset, Any]):
    """

    type: DictionarySearchOptionsOptionsAdditionalPropertyType
    default: Union[Unset, Any] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        type = self.type.value
        default = self.default

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
            }
        )
        if default is not UNSET:
            field_dict["default"] = default

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DictionarySearchOptionsOptionsAdditionalProperty` from a dict"""
        d = src_dict.copy()
        type = DictionarySearchOptionsOptionsAdditionalPropertyType(d.pop("type"))

        default = d.pop("default", UNSET)

        dictionary_search_options_options_additional_property = cls(
            type=type,
            default=default,
        )

        return dictionary_search_options_options_additional_property
