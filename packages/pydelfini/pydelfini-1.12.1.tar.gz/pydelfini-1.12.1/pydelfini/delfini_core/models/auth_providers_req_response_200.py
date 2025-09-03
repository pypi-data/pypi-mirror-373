from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.oauth_provider import OauthProvider


T = TypeVar("T", bound="AuthProvidersReqResponse200")


@_attrs_define
class AuthProvidersReqResponse200:
    """AuthProvidersReqResponse200 model"""

    additional_properties: Dict[str, "OauthProvider"] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AuthProvidersReqResponse200` from a dict"""
        d = src_dict.copy()
        auth_providers_req_response_200 = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = OauthProvider.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        auth_providers_req_response_200.additional_properties = additional_properties
        return auth_providers_req_response_200

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "OauthProvider":
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: "OauthProvider") -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
