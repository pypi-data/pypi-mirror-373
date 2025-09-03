from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="NewUser")


@_attrs_define
class NewUser:
    """NewUser model

    Attributes:
        given_name (str):
        last_name (str):
        password (str):
        user_email (str):
        user_name (str):
    """

    given_name: str
    last_name: str
    password: str
    user_email: str
    user_name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        given_name = self.given_name
        last_name = self.last_name
        password = self.password
        user_email = self.user_email
        user_name = self.user_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "given_name": given_name,
                "last_name": last_name,
                "password": password,
                "user_email": user_email,
                "user_name": user_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`NewUser` from a dict"""
        d = src_dict.copy()
        given_name = d.pop("given_name")

        last_name = d.pop("last_name")

        password = d.pop("password")

        user_email = d.pop("user_email")

        user_name = d.pop("user_name")

        new_user = cls(
            given_name=given_name,
            last_name=last_name,
            password=password,
            user_email=user_email,
            user_name=user_name,
        )

        return new_user
