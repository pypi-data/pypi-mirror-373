from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_element_permissible_values_date_time_format_date_time_format_format_type_0_isoformat import (
    DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0Isoformat,
)


T = TypeVar(
    "T", bound="DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0"
)


@_attrs_define
class DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0:
    """DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0 model

    Attributes:
        isoformat (DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0Isoformat): ISO 8601 standardized
            date/time formats
    """

    isoformat: DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0Isoformat

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        isoformat = self.isoformat.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "isoformat": isoformat,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0` from a dict"""
        d = src_dict.copy()
        isoformat = DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0Isoformat(
            d.pop("isoformat")
        )

        data_element_permissible_values_date_time_format_date_time_format_format_type_0 = cls(
            isoformat=isoformat,
        )

        return data_element_permissible_values_date_time_format_date_time_format_format_type_0
