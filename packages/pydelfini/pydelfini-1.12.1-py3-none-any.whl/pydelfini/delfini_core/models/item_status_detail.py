import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.error import Error
from ..models.item_status_value import ItemStatusValue


T = TypeVar("T", bound="ItemStatusDetail")


@_attrs_define
class ItemStatusDetail:
    """ItemStatusDetail model

    Attributes:
        errors (List['Error']):
        on (datetime.datetime):
        status (ItemStatusValue):
    """

    errors: List["Error"]
    on: datetime.datetime
    status: ItemStatusValue

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        on = self.on.isoformat()
        status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "errors": errors,
                "on": on,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`ItemStatusDetail` from a dict"""
        d = src_dict.copy()
        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = Error.from_dict(errors_item_data)

            errors.append(errors_item)

        on = isoparse(d.pop("on"))

        status = ItemStatusValue(d.pop("status"))

        item_status_detail = cls(
            errors=errors,
            on=on,
            status=status,
        )

        return item_status_detail
