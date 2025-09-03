from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="DataElementPermissibleValuesTextRangeTextRange")


@_attrs_define
class DataElementPermissibleValuesTextRangeTextRange:
    """Controls on the textual domain of the data.

    Attributes:
        max_length (Union[Unset, int]):
        meaning (Union[Unset, str]): A description of this range's meaning.
        min_length (Union[Unset, int]):
        regex (Union[Unset, str]): An optional regular expression that validates the data.
    """

    max_length: Union[Unset, int] = UNSET
    meaning: Union[Unset, str] = UNSET
    min_length: Union[Unset, int] = UNSET
    regex: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        max_length = self.max_length
        meaning = self.meaning
        min_length = self.min_length
        regex = self.regex

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if max_length is not UNSET:
            field_dict["maxLength"] = max_length
        if meaning is not UNSET:
            field_dict["meaning"] = meaning
        if min_length is not UNSET:
            field_dict["minLength"] = min_length
        if regex is not UNSET:
            field_dict["regex"] = regex

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesTextRangeTextRange` from a dict"""
        d = src_dict.copy()
        max_length = d.pop("maxLength", UNSET)

        meaning = d.pop("meaning", UNSET)

        min_length = d.pop("minLength", UNSET)

        regex = d.pop("regex", UNSET)

        data_element_permissible_values_text_range_text_range = cls(
            max_length=max_length,
            meaning=meaning,
            min_length=min_length,
            regex=regex,
        )

        return data_element_permissible_values_text_range_text_range
