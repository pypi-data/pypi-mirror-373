from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.metadata_field_group_resource import MetadataFieldGroupResource
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="MetadataFieldGroup")


@_attrs_define
class MetadataFieldGroup:
    """MetadataFieldGroup model

    Attributes:
        field_names (List[str]):
        id (str): Unique ID for the group
        resource (MetadataFieldGroupResource):
        title (str):
        description (Union[Unset, str]):
        edit_page (Union[Unset, bool]):
        view_position (Union[Unset, str]):
        visibility (Union[Unset, str]):
    """

    field_names: List[str]
    id: str
    resource: MetadataFieldGroupResource
    title: str
    description: Union[Unset, str] = UNSET
    edit_page: Union[Unset, bool] = UNSET
    view_position: Union[Unset, str] = UNSET
    visibility: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        field_names = self.field_names

        id = self.id
        resource = self.resource.value
        title = self.title
        description = self.description
        edit_page = self.edit_page
        view_position = self.view_position
        visibility = self.visibility

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "field_names": field_names,
                "id": id,
                "resource": resource,
                "title": title,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if edit_page is not UNSET:
            field_dict["edit_page"] = edit_page
        if view_position is not UNSET:
            field_dict["view_position"] = view_position
        if visibility is not UNSET:
            field_dict["visibility"] = visibility

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetadataFieldGroup` from a dict"""
        d = src_dict.copy()
        field_names = cast(List[str], d.pop("field_names"))

        id = d.pop("id")

        resource = MetadataFieldGroupResource(d.pop("resource"))

        title = d.pop("title")

        description = d.pop("description", UNSET)

        edit_page = d.pop("edit_page", UNSET)

        view_position = d.pop("view_position", UNSET)

        visibility = d.pop("visibility", UNSET)

        metadata_field_group = cls(
            field_names=field_names,
            id=id,
            resource=resource,
            title=title,
            description=description,
            edit_page=edit_page,
            view_position=view_position,
            visibility=visibility,
        )

        return metadata_field_group
