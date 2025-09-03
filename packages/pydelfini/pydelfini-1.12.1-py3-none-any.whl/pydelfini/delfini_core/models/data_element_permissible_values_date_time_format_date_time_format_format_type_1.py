from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar(
    "T", bound="DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType1"
)


@_attrs_define
class DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType1:
    """DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType1 model

    Attributes:
        strptime (str): Datetime parsing format string accepting
            percent-prefix format specifiers as in the
            standard strptime library function
    """

    strptime: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        strptime = self.strptime

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "strptime": strptime,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType1` from a dict"""
        d = src_dict.copy()
        strptime = d.pop("strptime")

        data_element_permissible_values_date_time_format_date_time_format_format_type_1 = cls(
            strptime=strptime,
        )

        return data_element_permissible_values_date_time_format_date_time_format_format_type_1
