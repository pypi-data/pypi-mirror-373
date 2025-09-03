from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_authentication_google_type import (
    SystemConfigurationAuthenticationGoogleType,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SystemConfigurationAuthenticationGoogle")


@_attrs_define
class SystemConfigurationAuthenticationGoogle:
    """SystemConfigurationAuthenticationGoogle model

    Attributes:
        client_id (str):
        client_secret (str):
        enabled (Union[Unset, bool]):  Default: False.
        type (Union[Unset, SystemConfigurationAuthenticationGoogleType]):
    """

    client_id: str
    client_secret: str
    enabled: Union[Unset, bool] = False
    type: Union[Unset, SystemConfigurationAuthenticationGoogleType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        client_id = self.client_id
        client_secret = self.client_secret
        enabled = self.enabled
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "client_id": client_id,
                "client_secret": client_secret,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationAuthenticationGoogle` from a dict"""
        d = src_dict.copy()
        client_id = d.pop("client_id")

        client_secret = d.pop("client_secret")

        enabled = d.pop("enabled", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, SystemConfigurationAuthenticationGoogleType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = SystemConfigurationAuthenticationGoogleType(_type)

        system_configuration_authentication_google = cls(
            client_id=client_id,
            client_secret=client_secret,
            enabled=enabled,
            type=type,
        )

        system_configuration_authentication_google.additional_properties = d
        return system_configuration_authentication_google

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
