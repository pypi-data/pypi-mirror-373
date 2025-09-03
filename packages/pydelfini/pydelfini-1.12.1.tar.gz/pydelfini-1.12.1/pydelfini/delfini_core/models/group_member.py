from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.group_role import GroupRole
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="GroupMember")


@_attrs_define
class GroupMember:
    """GroupMember model

    Attributes:
        role (GroupRole):
        user_id (str):
        group_id (Union[Unset, str]):
    """

    role: GroupRole
    user_id: str
    group_id: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        role = self.role.value
        user_id = self.user_id
        group_id = self.group_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "role": role,
                "user_id": user_id,
            }
        )
        if group_id is not UNSET:
            field_dict["group_id"] = group_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`GroupMember` from a dict"""
        d = src_dict.copy()
        role = GroupRole(d.pop("role"))

        user_id = d.pop("user_id")

        group_id = d.pop("group_id", UNSET)

        group_member = cls(
            role=role,
            user_id=user_id,
            group_id=group_id,
        )

        return group_member
