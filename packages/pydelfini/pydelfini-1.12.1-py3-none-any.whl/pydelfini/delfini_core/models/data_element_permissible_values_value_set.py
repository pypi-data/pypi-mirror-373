from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_element_permissible_values_value_set_value_set_item import (
    DataElementPermissibleValuesValueSetValueSetItem,
)


T = TypeVar("T", bound="DataElementPermissibleValuesValueSet")


@_attrs_define
class DataElementPermissibleValuesValueSet:
    """DataElementPermissibleValuesValueSet model

    Attributes:
        value_set (List['DataElementPermissibleValuesValueSetValueSetItem']): One or more values that exactly match the
            data.
    """

    value_set: List["DataElementPermissibleValuesValueSetValueSetItem"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        value_set = []
        for value_set_item_data in self.value_set:
            value_set_item = value_set_item_data.to_dict()
            value_set.append(value_set_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "valueSet": value_set,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesValueSet` from a dict"""
        d = src_dict.copy()
        value_set = []
        _value_set = d.pop("valueSet")
        for value_set_item_data in _value_set:
            value_set_item = DataElementPermissibleValuesValueSetValueSetItem.from_dict(
                value_set_item_data
            )

            value_set.append(value_set_item)

        data_element_permissible_values_value_set = cls(
            value_set=value_set,
        )

        return data_element_permissible_values_value_set
