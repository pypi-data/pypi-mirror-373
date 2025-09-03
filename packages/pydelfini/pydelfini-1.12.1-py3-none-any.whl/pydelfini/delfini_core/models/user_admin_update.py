from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="UserAdminUpdate")


@_attrs_define
class UserAdminUpdate:
    """UserAdminUpdate model

    Attributes:
        is_disabled (Union[Unset, bool]):
    """

    is_disabled: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        is_disabled = self.is_disabled

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_disabled is not UNSET:
            field_dict["is_disabled"] = is_disabled

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`UserAdminUpdate` from a dict"""
        d = src_dict.copy()
        is_disabled = d.pop("is_disabled", UNSET)

        user_admin_update = cls(
            is_disabled=is_disabled,
        )

        user_admin_update.additional_properties = d
        return user_admin_update

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
