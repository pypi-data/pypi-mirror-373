import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.group import Group
from ..models.user_metadata import UserMetadata
from ..models.visibility_level import VisibilityLevel
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """User model

    Attributes:
        account_id (str):
        created_on (datetime.datetime):
        metadata (UserMetadata):
        subject_id (str):
        user_name (str):
        visibility_level (VisibilityLevel):
        given_name (Union[Unset, str]):
        groups (Union[Unset, List['Group']]): Names and ids of the groups this user belongs to
        last_name (Union[Unset, str]):
        user_email (Union[Unset, str]):
    """

    account_id: str
    created_on: datetime.datetime
    metadata: "UserMetadata"
    subject_id: str
    user_name: str
    visibility_level: VisibilityLevel
    given_name: Union[Unset, str] = UNSET
    groups: Union[Unset, List["Group"]] = UNSET
    last_name: Union[Unset, str] = UNSET
    user_email: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        account_id = self.account_id
        created_on = self.created_on.isoformat()
        metadata = self.metadata.to_dict()
        subject_id = self.subject_id
        user_name = self.user_name
        visibility_level = self.visibility_level.value
        given_name = self.given_name
        groups: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = []
            for groups_item_data in self.groups:
                groups_item = groups_item_data.to_dict()
                groups.append(groups_item)

        last_name = self.last_name
        user_email = self.user_email

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "account_id": account_id,
                "created_on": created_on,
                "metadata": metadata,
                "subject_id": subject_id,
                "user_name": user_name,
                "visibility_level": visibility_level,
            }
        )
        if given_name is not UNSET:
            field_dict["given_name"] = given_name
        if groups is not UNSET:
            field_dict["groups"] = groups
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if user_email is not UNSET:
            field_dict["user_email"] = user_email

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`User` from a dict"""
        d = src_dict.copy()
        account_id = d.pop("account_id")

        created_on = isoparse(d.pop("created_on"))

        metadata = UserMetadata.from_dict(d.pop("metadata"))

        subject_id = d.pop("subject_id")

        user_name = d.pop("user_name")

        visibility_level = VisibilityLevel(d.pop("visibility_level"))

        given_name = d.pop("given_name", UNSET)

        groups = []
        _groups = d.pop("groups", UNSET)
        for groups_item_data in _groups or []:
            groups_item = Group.from_dict(groups_item_data)

            groups.append(groups_item)

        last_name = d.pop("last_name", UNSET)

        user_email = d.pop("user_email", UNSET)

        user = cls(
            account_id=account_id,
            created_on=created_on,
            metadata=metadata,
            subject_id=subject_id,
            user_name=user_name,
            visibility_level=visibility_level,
            given_name=given_name,
            groups=groups,
            last_name=last_name,
            user_email=user_email,
        )

        return user
