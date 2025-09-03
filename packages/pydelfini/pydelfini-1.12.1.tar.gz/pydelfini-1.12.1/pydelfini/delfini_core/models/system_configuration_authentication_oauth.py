from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_authentication_oauth_type import (
    SystemConfigurationAuthenticationOauthType,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SystemConfigurationAuthenticationOauth")


@_attrs_define
class SystemConfigurationAuthenticationOauth:
    """SystemConfigurationAuthenticationOauth model

    Attributes:
        authorization_url (str):
        base_url (str):
        client_id (str):
        client_secret (str):
        title (str):
        token_url (str):
        userinfo_url (str):
        enabled (Union[Unset, bool]):  Default: False.
        icon_url (Union[Unset, str]):
        type (Union[Unset, SystemConfigurationAuthenticationOauthType]):
    """

    authorization_url: str
    base_url: str
    client_id: str
    client_secret: str
    title: str
    token_url: str
    userinfo_url: str
    enabled: Union[Unset, bool] = False
    icon_url: Union[Unset, str] = UNSET
    type: Union[Unset, SystemConfigurationAuthenticationOauthType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        authorization_url = self.authorization_url
        base_url = self.base_url
        client_id = self.client_id
        client_secret = self.client_secret
        title = self.title
        token_url = self.token_url
        userinfo_url = self.userinfo_url
        enabled = self.enabled
        icon_url = self.icon_url
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authorization_url": authorization_url,
                "base_url": base_url,
                "client_id": client_id,
                "client_secret": client_secret,
                "title": title,
                "token_url": token_url,
                "userinfo_url": userinfo_url,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationAuthenticationOauth` from a dict"""
        d = src_dict.copy()
        authorization_url = d.pop("authorization_url")

        base_url = d.pop("base_url")

        client_id = d.pop("client_id")

        client_secret = d.pop("client_secret")

        title = d.pop("title")

        token_url = d.pop("token_url")

        userinfo_url = d.pop("userinfo_url")

        enabled = d.pop("enabled", UNSET)

        icon_url = d.pop("icon_url", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, SystemConfigurationAuthenticationOauthType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = SystemConfigurationAuthenticationOauthType(_type)

        system_configuration_authentication_oauth = cls(
            authorization_url=authorization_url,
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            title=title,
            token_url=token_url,
            userinfo_url=userinfo_url,
            enabled=enabled,
            icon_url=icon_url,
            type=type,
        )

        system_configuration_authentication_oauth.additional_properties = d
        return system_configuration_authentication_oauth

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
