from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="DataElementPermissibleValuesNumberRangeNumberRange")


@_attrs_define
class DataElementPermissibleValuesNumberRangeNumberRange:
    """Controls on the numerical domain of the data.

    Attributes:
        is_integer (Union[Unset, bool]): True if the number should be an integer.
        maximum (Union[Unset, float]):
        meaning (Union[Unset, str]): A description of this range's meaning.
        minimum (Union[Unset, float]):
    """

    is_integer: Union[Unset, bool] = UNSET
    maximum: Union[Unset, float] = UNSET
    meaning: Union[Unset, str] = UNSET
    minimum: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        is_integer = self.is_integer
        maximum = self.maximum
        meaning = self.meaning
        minimum = self.minimum

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if is_integer is not UNSET:
            field_dict["isInteger"] = is_integer
        if maximum is not UNSET:
            field_dict["maximum"] = maximum
        if meaning is not UNSET:
            field_dict["meaning"] = meaning
        if minimum is not UNSET:
            field_dict["minimum"] = minimum

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesNumberRangeNumberRange` from a dict"""
        d = src_dict.copy()
        is_integer = d.pop("isInteger", UNSET)

        maximum = d.pop("maximum", UNSET)

        meaning = d.pop("meaning", UNSET)

        minimum = d.pop("minimum", UNSET)

        data_element_permissible_values_number_range_number_range = cls(
            is_integer=is_integer,
            maximum=maximum,
            meaning=meaning,
            minimum=minimum,
        )

        return data_element_permissible_values_number_range_number_range
