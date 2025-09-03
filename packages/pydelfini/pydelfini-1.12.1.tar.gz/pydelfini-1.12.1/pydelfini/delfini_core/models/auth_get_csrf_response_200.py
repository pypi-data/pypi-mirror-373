from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="AuthGetCsrfResponse200")


@_attrs_define
class AuthGetCsrfResponse200:
    """AuthGetCsrfResponse200 model

    Attributes:
        csrf_token (str):
    """

    csrf_token: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        csrf_token = self.csrf_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "csrfToken": csrf_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AuthGetCsrfResponse200` from a dict"""
        d = src_dict.copy()
        csrf_token = d.pop("csrfToken")

        auth_get_csrf_response_200 = cls(
            csrf_token=csrf_token,
        )

        return auth_get_csrf_response_200
