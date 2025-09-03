from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.group_create_group_body_metadata import GroupCreateGroupBodyMetadata
from ..models.visibility_level import VisibilityLevel
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="GroupCreateGroupBody")


@_attrs_define
class GroupCreateGroupBody:
    """GroupCreateGroupBody model

    Attributes:
        name (str):
        controlled_access (Union[Unset, bool]):  Default: False.
        metadata (Union[Unset, GroupCreateGroupBodyMetadata]):
        visibility_level (Union[Unset, VisibilityLevel]):
    """

    name: str
    controlled_access: Union[Unset, bool] = False
    metadata: Union[Unset, "GroupCreateGroupBodyMetadata"] = UNSET
    visibility_level: Union[Unset, VisibilityLevel] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        name = self.name
        controlled_access = self.controlled_access
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        visibility_level: Union[Unset, str] = UNSET
        if not isinstance(self.visibility_level, Unset):
            visibility_level = self.visibility_level.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
            }
        )
        if controlled_access is not UNSET:
            field_dict["controlledAccess"] = controlled_access
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if visibility_level is not UNSET:
            field_dict["visibilityLevel"] = visibility_level

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`GroupCreateGroupBody` from a dict"""
        d = src_dict.copy()
        name = d.pop("name")

        controlled_access = d.pop("controlledAccess", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, GroupCreateGroupBodyMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = GroupCreateGroupBodyMetadata.from_dict(_metadata)

        _visibility_level = d.pop("visibilityLevel", UNSET)
        visibility_level: Union[Unset, VisibilityLevel]
        if isinstance(_visibility_level, Unset):
            visibility_level = UNSET
        else:
            visibility_level = VisibilityLevel(_visibility_level)

        group_create_group_body = cls(
            name=name,
            controlled_access=controlled_access,
            metadata=metadata,
            visibility_level=visibility_level,
        )

        return group_create_group_body
