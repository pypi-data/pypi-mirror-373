from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.metadata_field import MetadataField
from ..models.metadata_field_group import MetadataFieldGroup
from ..models.metadata_field_groups_data_elements import MetadataFieldGroupsDataElements
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="MetadataFieldGroups")


@_attrs_define
class MetadataFieldGroups:
    """MetadataFieldGroups model

    Attributes:
        fields (List['MetadataField']):
        groups (List['MetadataFieldGroup']):
        data_elements (Union[Unset, MetadataFieldGroupsDataElements]):
    """

    fields: List["MetadataField"]
    groups: List["MetadataFieldGroup"]
    data_elements: Union[Unset, "MetadataFieldGroupsDataElements"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        fields = []
        for fields_item_data in self.fields:
            fields_item = fields_item_data.to_dict()
            fields.append(fields_item)

        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)

        data_elements: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.data_elements, Unset):
            data_elements = self.data_elements.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "fields": fields,
                "groups": groups,
            }
        )
        if data_elements is not UNSET:
            field_dict["data_elements"] = data_elements

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetadataFieldGroups` from a dict"""
        d = src_dict.copy()
        fields = []
        _fields = d.pop("fields")
        for fields_item_data in _fields:
            fields_item = MetadataField.from_dict(fields_item_data)

            fields.append(fields_item)

        groups = []
        _groups = d.pop("groups")
        for groups_item_data in _groups:
            groups_item = MetadataFieldGroup.from_dict(groups_item_data)

            groups.append(groups_item)

        _data_elements = d.pop("data_elements", UNSET)
        data_elements: Union[Unset, MetadataFieldGroupsDataElements]
        if isinstance(_data_elements, Unset):
            data_elements = UNSET
        else:
            data_elements = MetadataFieldGroupsDataElements.from_dict(_data_elements)

        metadata_field_groups = cls(
            fields=fields,
            groups=groups,
            data_elements=data_elements,
        )

        return metadata_field_groups
