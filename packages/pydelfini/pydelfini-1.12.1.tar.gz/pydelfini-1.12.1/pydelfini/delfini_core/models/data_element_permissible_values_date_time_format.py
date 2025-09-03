from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_element_permissible_values_date_time_format_date_time_format import (
    DataElementPermissibleValuesDateTimeFormatDateTimeFormat,
)


T = TypeVar("T", bound="DataElementPermissibleValuesDateTimeFormat")


@_attrs_define
class DataElementPermissibleValuesDateTimeFormat:
    """DataElementPermissibleValuesDateTimeFormat model

    Attributes:
        date_time_format (DataElementPermissibleValuesDateTimeFormatDateTimeFormat): Controls on the date, time or
            duration domain of the data.
    """

    date_time_format: "DataElementPermissibleValuesDateTimeFormatDateTimeFormat"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        date_time_format = self.date_time_format.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dateTimeFormat": date_time_format,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesDateTimeFormat` from a dict"""
        d = src_dict.copy()
        date_time_format = (
            DataElementPermissibleValuesDateTimeFormatDateTimeFormat.from_dict(
                d.pop("dateTimeFormat")
            )
        )

        data_element_permissible_values_date_time_format = cls(
            date_time_format=date_time_format,
        )

        return data_element_permissible_values_date_time_format
