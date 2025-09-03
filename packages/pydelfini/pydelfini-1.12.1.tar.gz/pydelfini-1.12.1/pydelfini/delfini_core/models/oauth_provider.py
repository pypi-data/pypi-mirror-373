from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="OauthProvider")


@_attrs_define
class OauthProvider:
    """OauthProvider model

    Attributes:
        callback_url (str):
        id (str):
        name (str):
        signin_url (str):
        type (str):
        icon_url (Union[Unset, str]):
    """

    callback_url: str
    id: str
    name: str
    signin_url: str
    type: str
    icon_url: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        callback_url = self.callback_url
        id = self.id
        name = self.name
        signin_url = self.signin_url
        type = self.type
        icon_url = self.icon_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "callbackUrl": callback_url,
                "id": id,
                "name": name,
                "signinUrl": signin_url,
                "type": type,
            }
        )
        if icon_url is not UNSET:
            field_dict["iconUrl"] = icon_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`OauthProvider` from a dict"""
        d = src_dict.copy()
        callback_url = d.pop("callbackUrl")

        id = d.pop("id")

        name = d.pop("name")

        signin_url = d.pop("signinUrl")

        type = d.pop("type")

        icon_url = d.pop("iconUrl", UNSET)

        oauth_provider = cls(
            callback_url=callback_url,
            id=id,
            name=name,
            signin_url=signin_url,
            type=type,
            icon_url=icon_url,
        )

        return oauth_provider
