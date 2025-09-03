from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_element_permissible_values_number_range_number_range import (
    DataElementPermissibleValuesNumberRangeNumberRange,
)


T = TypeVar("T", bound="DataElementPermissibleValuesNumberRange")


@_attrs_define
class DataElementPermissibleValuesNumberRange:
    """DataElementPermissibleValuesNumberRange model

    Attributes:
        number_range (DataElementPermissibleValuesNumberRangeNumberRange): Controls on the numerical domain of the data.
    """

    number_range: "DataElementPermissibleValuesNumberRangeNumberRange"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        number_range = self.number_range.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "numberRange": number_range,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesNumberRange` from a dict"""
        d = src_dict.copy()
        number_range = DataElementPermissibleValuesNumberRangeNumberRange.from_dict(
            d.pop("numberRange")
        )

        data_element_permissible_values_number_range = cls(
            number_range=number_range,
        )

        return data_element_permissible_values_number_range
