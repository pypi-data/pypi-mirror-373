from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.data_element_permissible_values_date_time_format_date_time_format_format_type_0 import (
    DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0,
)
from ..models.data_element_permissible_values_date_time_format_date_time_format_format_type_1 import (
    DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType1,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="DataElementPermissibleValuesDateTimeFormatDateTimeFormat")


@_attrs_define
class DataElementPermissibleValuesDateTimeFormatDateTimeFormat:
    """Controls on the date, time or duration domain of the data.

    Attributes:
        format_ (Union['DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0',
            'DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType1']):
        meaning (Union[Unset, str]): A description of this format's meaning.
    """

    format_: Union[
        "DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0",
        "DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType1",
    ]
    meaning: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        format_: Dict[str, Any]
        if isinstance(
            self.format_,
            DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0,
        ):
            format_ = self.format_.to_dict()
        else:
            format_ = self.format_.to_dict()

        meaning = self.meaning

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "format": format_,
            }
        )
        if meaning is not UNSET:
            field_dict["meaning"] = meaning

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesDateTimeFormatDateTimeFormat` from a dict"""
        d = src_dict.copy()

        def _parse_format_(
            data: object,
        ) -> Union[
            "DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0",
            "DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType1",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                format_type_0 = DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0.from_dict(
                    data
                )

                return format_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            format_type_1 = DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType1.from_dict(
                data
            )

            return format_type_1

        format_ = _parse_format_(d.pop("format"))

        meaning = d.pop("meaning", UNSET)

        data_element_permissible_values_date_time_format_date_time_format = cls(
            format_=format_,
            meaning=meaning,
        )

        return data_element_permissible_values_date_time_format_date_time_format
