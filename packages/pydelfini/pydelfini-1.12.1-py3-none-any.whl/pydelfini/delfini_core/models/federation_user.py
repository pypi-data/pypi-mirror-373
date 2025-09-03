from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.federation_user_type import FederationUserType
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="FederationUser")


@_attrs_define
class FederationUser:
    """FederationUser model

    Attributes:
        followers (Union[Unset, str]):
        following (Union[Unset, str]):
        inbox (Union[Unset, str]):
        likes (Union[Unset, str]):
        outbox (Union[Unset, str]):
        preferred_username (Union[Unset, str]):
        type (Union[Unset, FederationUserType]):
    """

    followers: Union[Unset, str] = UNSET
    following: Union[Unset, str] = UNSET
    inbox: Union[Unset, str] = UNSET
    likes: Union[Unset, str] = UNSET
    outbox: Union[Unset, str] = UNSET
    preferred_username: Union[Unset, str] = UNSET
    type: Union[Unset, FederationUserType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        followers = self.followers
        following = self.following
        inbox = self.inbox
        likes = self.likes
        outbox = self.outbox
        preferred_username = self.preferred_username
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if followers is not UNSET:
            field_dict["followers"] = followers
        if following is not UNSET:
            field_dict["following"] = following
        if inbox is not UNSET:
            field_dict["inbox"] = inbox
        if likes is not UNSET:
            field_dict["likes"] = likes
        if outbox is not UNSET:
            field_dict["outbox"] = outbox
        if preferred_username is not UNSET:
            field_dict["preferredUsername"] = preferred_username
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`FederationUser` from a dict"""
        d = src_dict.copy()
        followers = d.pop("followers", UNSET)

        following = d.pop("following", UNSET)

        inbox = d.pop("inbox", UNSET)

        likes = d.pop("likes", UNSET)

        outbox = d.pop("outbox", UNSET)

        preferred_username = d.pop("preferredUsername", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, FederationUserType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = FederationUserType(_type)

        federation_user = cls(
            followers=followers,
            following=following,
            inbox=inbox,
            likes=likes,
            outbox=outbox,
            preferred_username=preferred_username,
            type=type,
        )

        federation_user.additional_properties = d
        return federation_user

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
