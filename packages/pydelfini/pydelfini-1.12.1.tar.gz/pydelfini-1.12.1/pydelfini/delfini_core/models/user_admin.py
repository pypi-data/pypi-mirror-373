import datetime
from typing import Any
from typing import cast
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="UserAdmin")


@_attrs_define
class UserAdmin:
    """User administrative settings

    Attributes:
        disabled_on (Union[None, Unset, datetime.datetime]):
    """

    disabled_on: Union[None, Unset, datetime.datetime] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        disabled_on: Union[None, Unset, str]
        if isinstance(self.disabled_on, Unset):
            disabled_on = UNSET
        elif isinstance(self.disabled_on, datetime.datetime):
            disabled_on = self.disabled_on.isoformat()
        else:
            disabled_on = self.disabled_on

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if disabled_on is not UNSET:
            field_dict["disabled_on"] = disabled_on

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`UserAdmin` from a dict"""
        d = src_dict.copy()

        def _parse_disabled_on(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                disabled_on_type_0 = isoparse(data)

                return disabled_on_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        disabled_on = _parse_disabled_on(d.pop("disabled_on", UNSET))

        user_admin = cls(
            disabled_on=disabled_on,
        )

        return user_admin
