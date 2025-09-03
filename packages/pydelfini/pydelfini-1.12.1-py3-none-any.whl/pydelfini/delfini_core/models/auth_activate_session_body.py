from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="AuthActivateSessionBody")


@_attrs_define
class AuthActivateSessionBody:
    """AuthActivateSessionBody model

    Attributes:
        activation_code (str):
    """

    activation_code: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        activation_code = self.activation_code

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "activation_code": activation_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AuthActivateSessionBody` from a dict"""
        d = src_dict.copy()
        activation_code = d.pop("activation_code")

        auth_activate_session_body = cls(
            activation_code=activation_code,
        )

        return auth_activate_session_body
