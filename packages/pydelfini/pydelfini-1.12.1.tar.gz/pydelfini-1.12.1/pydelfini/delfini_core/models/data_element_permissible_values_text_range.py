from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_element_permissible_values_text_range_text_range import (
    DataElementPermissibleValuesTextRangeTextRange,
)


T = TypeVar("T", bound="DataElementPermissibleValuesTextRange")


@_attrs_define
class DataElementPermissibleValuesTextRange:
    """DataElementPermissibleValuesTextRange model

    Attributes:
        text_range (DataElementPermissibleValuesTextRangeTextRange): Controls on the textual domain of the data.
    """

    text_range: "DataElementPermissibleValuesTextRangeTextRange"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        text_range = self.text_range.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "textRange": text_range,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesTextRange` from a dict"""
        d = src_dict.copy()
        text_range = DataElementPermissibleValuesTextRangeTextRange.from_dict(
            d.pop("textRange")
        )

        data_element_permissible_values_text_range = cls(
            text_range=text_range,
        )

        return data_element_permissible_values_text_range
