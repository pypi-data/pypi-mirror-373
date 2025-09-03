from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.update_project_metadata import UpdateProjectMetadata
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="UpdateProject")


@_attrs_define
class UpdateProject:
    """UpdateProject model

    Attributes:
        description (Union[Unset, str]):
        metadata (Union[Unset, UpdateProjectMetadata]):
        name (Union[Unset, str]):
    """

    description: Union[Unset, str] = UNSET
    metadata: Union[Unset, "UpdateProjectMetadata"] = UNSET
    name: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        description = self.description
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`UpdateProject` from a dict"""
        d = src_dict.copy()
        description = d.pop("description", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, UpdateProjectMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateProjectMetadata.from_dict(_metadata)

        name = d.pop("name", UNSET)

        update_project = cls(
            description=description,
            metadata=metadata,
            name=name,
        )

        return update_project
