from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.metadata_field_group import MetadataFieldGroup


T = TypeVar("T", bound="MetadataSetFieldGroupsBody")


@_attrs_define
class MetadataSetFieldGroupsBody:
    """MetadataSetFieldGroupsBody model

    Attributes:
        groups (List['MetadataFieldGroup']):
    """

    groups: List["MetadataFieldGroup"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "groups": groups,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetadataSetFieldGroupsBody` from a dict"""
        d = src_dict.copy()
        groups = []
        _groups = d.pop("groups")
        for groups_item_data in _groups:
            groups_item = MetadataFieldGroup.from_dict(groups_item_data)

            groups.append(groups_item)

        metadata_set_field_groups_body = cls(
            groups=groups,
        )

        return metadata_set_field_groups_body
