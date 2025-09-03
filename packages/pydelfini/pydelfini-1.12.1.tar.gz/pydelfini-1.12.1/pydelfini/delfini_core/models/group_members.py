from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.group_member import GroupMember
from ..models.group_members_users import GroupMembersUsers
from ..models.pagination import Pagination
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="GroupMembers")


@_attrs_define
class GroupMembers:
    """GroupMembers model

    Attributes:
        members (List['GroupMember']):
        pagination (Pagination):
        users (Union[Unset, GroupMembersUsers]):
    """

    members: List["GroupMember"]
    pagination: "Pagination"
    users: Union[Unset, "GroupMembersUsers"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        members = []
        for members_item_data in self.members:
            members_item = members_item_data.to_dict()
            members.append(members_item)

        pagination = self.pagination.to_dict()
        users: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.users, Unset):
            users = self.users.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "members": members,
                "pagination": pagination,
            }
        )
        if users is not UNSET:
            field_dict["users"] = users

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`GroupMembers` from a dict"""
        d = src_dict.copy()
        members = []
        _members = d.pop("members")
        for members_item_data in _members:
            members_item = GroupMember.from_dict(members_item_data)

            members.append(members_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        _users = d.pop("users", UNSET)
        users: Union[Unset, GroupMembersUsers]
        if isinstance(_users, Unset):
            users = UNSET
        else:
            users = GroupMembersUsers.from_dict(_users)

        group_members = cls(
            members=members,
            pagination=pagination,
            users=users,
        )

        return group_members
