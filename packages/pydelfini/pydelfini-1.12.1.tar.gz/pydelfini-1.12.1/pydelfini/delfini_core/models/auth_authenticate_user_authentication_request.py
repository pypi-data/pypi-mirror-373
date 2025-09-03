from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="AuthAuthenticateUserAuthenticationRequest")


@_attrs_define
class AuthAuthenticateUserAuthenticationRequest:
    """AuthAuthenticateUserAuthenticationRequest model

    Attributes:
        callback_url (str):
        csrf_token (str):
        password (str):
        user_name (str):
        json (Union[Unset, bool]):  Default: True.
        redirect (Union[Unset, bool]):  Default: True.
    """

    callback_url: str
    csrf_token: str
    password: str
    user_name: str
    json: Union[Unset, bool] = True
    redirect: Union[Unset, bool] = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        callback_url = self.callback_url
        csrf_token = self.csrf_token
        password = self.password
        user_name = self.user_name
        json = self.json
        redirect = self.redirect

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "callbackUrl": callback_url,
                "csrfToken": csrf_token,
                "password": password,
                "user_name": user_name,
            }
        )
        if json is not UNSET:
            field_dict["json"] = json
        if redirect is not UNSET:
            field_dict["redirect"] = redirect

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AuthAuthenticateUserAuthenticationRequest` from a dict"""
        d = src_dict.copy()
        callback_url = d.pop("callbackUrl")

        csrf_token = d.pop("csrfToken")

        password = d.pop("password")

        user_name = d.pop("user_name")

        json = d.pop("json", UNSET)

        redirect = d.pop("redirect", UNSET)

        auth_authenticate_user_authentication_request = cls(
            callback_url=callback_url,
            csrf_token=csrf_token,
            password=password,
            user_name=user_name,
            json=json,
            redirect=redirect,
        )

        return auth_authenticate_user_authentication_request
