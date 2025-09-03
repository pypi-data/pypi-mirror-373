from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="AuthSignoutNoData")


@_attrs_define
class AuthSignoutNoData:
    """AuthSignoutNoData model"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AuthSignoutNoData` from a dict"""
        src_dict.copy()
        auth_signout_no_data = cls()

        return auth_signout_no_data
