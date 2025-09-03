from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="AuthProviderSigninProviderResponse200")


@_attrs_define
class AuthProviderSigninProviderResponse200:
    """AuthProviderSigninProviderResponse200 model

    Attributes:
        url (str):
    """

    url: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "url": url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AuthProviderSigninProviderResponse200` from a dict"""
        d = src_dict.copy()
        url = d.pop("url")

        auth_provider_signin_provider_response_200 = cls(
            url=url,
        )

        return auth_provider_signin_provider_response_200
