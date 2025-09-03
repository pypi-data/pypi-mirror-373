from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_authentication_credentials import (
    SystemConfigurationAuthenticationCredentials,
)
from ..models.system_configuration_authentication_github import (
    SystemConfigurationAuthenticationGithub,
)
from ..models.system_configuration_authentication_google import (
    SystemConfigurationAuthenticationGoogle,
)
from ..models.system_configuration_authentication_oauth import (
    SystemConfigurationAuthenticationOauth,
)


T = TypeVar("T", bound="SystemConfigurationAuthentication")


@_attrs_define
class SystemConfigurationAuthentication:
    """SystemConfigurationAuthentication model"""

    additional_properties: Dict[
        str,
        Union[
            "SystemConfigurationAuthenticationCredentials",
            "SystemConfigurationAuthenticationGithub",
            "SystemConfigurationAuthenticationGoogle",
            "SystemConfigurationAuthenticationOauth",
        ],
    ] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, SystemConfigurationAuthenticationCredentials):
                field_dict[prop_name] = prop.to_dict()
            elif isinstance(prop, SystemConfigurationAuthenticationOauth):
                field_dict[prop_name] = prop.to_dict()
            elif isinstance(prop, SystemConfigurationAuthenticationGithub):
                field_dict[prop_name] = prop.to_dict()
            else:
                field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationAuthentication` from a dict"""
        d = src_dict.copy()
        system_configuration_authentication = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(
                data: object,
            ) -> Union[
                "SystemConfigurationAuthenticationCredentials",
                "SystemConfigurationAuthenticationGithub",
                "SystemConfigurationAuthenticationGoogle",
                "SystemConfigurationAuthenticationOauth",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_0 = (
                        SystemConfigurationAuthenticationCredentials.from_dict(data)
                    )

                    return additional_property_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_1 = (
                        SystemConfigurationAuthenticationOauth.from_dict(data)
                    )

                    return additional_property_type_1
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_2 = (
                        SystemConfigurationAuthenticationGithub.from_dict(data)
                    )

                    return additional_property_type_2
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                additional_property_type_3 = (
                    SystemConfigurationAuthenticationGoogle.from_dict(data)
                )

                return additional_property_type_3

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        system_configuration_authentication.additional_properties = (
            additional_properties
        )
        return system_configuration_authentication

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(
        self, key: str
    ) -> Union[
        "SystemConfigurationAuthenticationCredentials",
        "SystemConfigurationAuthenticationGithub",
        "SystemConfigurationAuthenticationGoogle",
        "SystemConfigurationAuthenticationOauth",
    ]:
        return self.additional_properties[key]

    def __setitem__(
        self,
        key: str,
        value: Union[
            "SystemConfigurationAuthenticationCredentials",
            "SystemConfigurationAuthenticationGithub",
            "SystemConfigurationAuthenticationGoogle",
            "SystemConfigurationAuthenticationOauth",
        ],
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
