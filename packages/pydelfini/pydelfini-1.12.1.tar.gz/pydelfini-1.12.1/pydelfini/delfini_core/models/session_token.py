from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="SessionToken")


@_attrs_define
class SessionToken:
    """SessionToken model

    Attributes:
        activation_code (str):
        session_id (str):
    """

    activation_code: str
    session_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        activation_code = self.activation_code
        session_id = self.session_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "activation_code": activation_code,
                "session_id": session_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SessionToken` from a dict"""
        d = src_dict.copy()
        activation_code = d.pop("activation_code")

        session_id = d.pop("session_id")

        session_token = cls(
            activation_code=activation_code,
            session_id=session_id,
        )

        return session_token
