from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_role import GroupRole


T = TypeVar("T", bound="GroupGetGroupsResponse200SelfRoles")


@_attrs_define
class GroupGetGroupsResponse200SelfRoles:
    """GroupGetGroupsResponse200SelfRoles model"""

    additional_properties: Dict[str, GroupRole] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.value
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`GroupGetGroupsResponse200SelfRoles` from a dict"""
        d = src_dict.copy()
        group_get_groups_response_200_self_roles = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = GroupRole(prop_dict)

            additional_properties[prop_name] = additional_property

        group_get_groups_response_200_self_roles.additional_properties = (
            additional_properties
        )
        return group_get_groups_response_200_self_roles

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> GroupRole:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: GroupRole) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
