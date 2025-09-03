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


T = TypeVar("T", bound="SystemConfigurationSessions")


@_attrs_define
class SystemConfigurationSessions:
    """SystemConfigurationSessions model

    Attributes:
        persistent (Union[Unset, bool]):  Default: True.
        persistent_lifetime (Union[Unset, int]):  Default: 1209600.
    """

    persistent: Union[Unset, bool] = True
    persistent_lifetime: Union[Unset, int] = 1209600
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        persistent = self.persistent
        persistent_lifetime = self.persistent_lifetime

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if persistent is not UNSET:
            field_dict["persistent"] = persistent
        if persistent_lifetime is not UNSET:
            field_dict["persistent_lifetime"] = persistent_lifetime

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationSessions` from a dict"""
        d = src_dict.copy()
        persistent = d.pop("persistent", UNSET)

        persistent_lifetime = d.pop("persistent_lifetime", UNSET)

        system_configuration_sessions = cls(
            persistent=persistent,
            persistent_lifetime=persistent_lifetime,
        )

        system_configuration_sessions.additional_properties = d
        return system_configuration_sessions

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
