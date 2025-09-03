from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_authentication_credentials_type import (
    SystemConfigurationAuthenticationCredentialsType,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SystemConfigurationAuthenticationCredentials")


@_attrs_define
class SystemConfigurationAuthenticationCredentials:
    """SystemConfigurationAuthenticationCredentials model

    Attributes:
        admin_only (Union[Unset, bool]):  Default: False.
        enabled (Union[Unset, bool]):  Default: True.
        type (Union[Unset, SystemConfigurationAuthenticationCredentialsType]):
    """

    admin_only: Union[Unset, bool] = False
    enabled: Union[Unset, bool] = True
    type: Union[Unset, SystemConfigurationAuthenticationCredentialsType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        admin_only = self.admin_only
        enabled = self.enabled
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if admin_only is not UNSET:
            field_dict["admin_only"] = admin_only
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationAuthenticationCredentials` from a dict"""
        d = src_dict.copy()
        admin_only = d.pop("admin_only", UNSET)

        enabled = d.pop("enabled", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, SystemConfigurationAuthenticationCredentialsType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = SystemConfigurationAuthenticationCredentialsType(_type)

        system_configuration_authentication_credentials = cls(
            admin_only=admin_only,
            enabled=enabled,
            type=type,
        )

        system_configuration_authentication_credentials.additional_properties = d
        return system_configuration_authentication_credentials

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
