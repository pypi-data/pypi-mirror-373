import datetime
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.session_user import SessionUser


T = TypeVar("T", bound="AuthGetSessionResponse200")


@_attrs_define
class AuthGetSessionResponse200:
    """AuthGetSessionResponse200 model

    Attributes:
        expires (datetime.datetime):
        user (SessionUser):
    """

    expires: datetime.datetime
    user: "SessionUser"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        expires = self.expires.isoformat()
        user = self.user.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "expires": expires,
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AuthGetSessionResponse200` from a dict"""
        d = src_dict.copy()
        expires = isoparse(d.pop("expires"))

        user = SessionUser.from_dict(d.pop("user"))

        auth_get_session_response_200 = cls(
            expires=expires,
            user=user,
        )

        return auth_get_session_response_200
