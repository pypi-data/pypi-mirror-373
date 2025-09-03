from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.group_update_group_body_metadata import GroupUpdateGroupBodyMetadata
from ..models.visibility_level import VisibilityLevel
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="GroupUpdateGroupBody")


@_attrs_define
class GroupUpdateGroupBody:
    """GroupUpdateGroupBody model

    Attributes:
        metadata (Union[Unset, GroupUpdateGroupBodyMetadata]):
        name (Union[Unset, str]):
        visibility_level (Union[Unset, VisibilityLevel]):
    """

    metadata: Union[Unset, "GroupUpdateGroupBodyMetadata"] = UNSET
    name: Union[Unset, str] = UNSET
    visibility_level: Union[Unset, VisibilityLevel] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        name = self.name
        visibility_level: Union[Unset, str] = UNSET
        if not isinstance(self.visibility_level, Unset):
            visibility_level = self.visibility_level.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if name is not UNSET:
            field_dict["name"] = name
        if visibility_level is not UNSET:
            field_dict["visibilityLevel"] = visibility_level

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`GroupUpdateGroupBody` from a dict"""
        d = src_dict.copy()
        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, GroupUpdateGroupBodyMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = GroupUpdateGroupBodyMetadata.from_dict(_metadata)

        name = d.pop("name", UNSET)

        _visibility_level = d.pop("visibilityLevel", UNSET)
        visibility_level: Union[Unset, VisibilityLevel]
        if isinstance(_visibility_level, Unset):
            visibility_level = UNSET
        else:
            visibility_level = VisibilityLevel(_visibility_level)

        group_update_group_body = cls(
            metadata=metadata,
            name=name,
            visibility_level=visibility_level,
        )

        return group_update_group_body
