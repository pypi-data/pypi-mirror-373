from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.metadata_field import MetadataField
from ..models.metadata_fields_data_elements import MetadataFieldsDataElements
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="MetadataFields")


@_attrs_define
class MetadataFields:
    """MetadataFields model

    Attributes:
        fields (List['MetadataField']):
        data_elements (Union[Unset, MetadataFieldsDataElements]):
    """

    fields: List["MetadataField"]
    data_elements: Union[Unset, "MetadataFieldsDataElements"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        fields = []
        for fields_item_data in self.fields:
            fields_item = fields_item_data.to_dict()
            fields.append(fields_item)

        data_elements: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.data_elements, Unset):
            data_elements = self.data_elements.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "fields": fields,
            }
        )
        if data_elements is not UNSET:
            field_dict["data_elements"] = data_elements

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetadataFields` from a dict"""
        d = src_dict.copy()
        fields = []
        _fields = d.pop("fields")
        for fields_item_data in _fields:
            fields_item = MetadataField.from_dict(fields_item_data)

            fields.append(fields_item)

        _data_elements = d.pop("data_elements", UNSET)
        data_elements: Union[Unset, MetadataFieldsDataElements]
        if isinstance(_data_elements, Unset):
            data_elements = UNSET
        else:
            data_elements = MetadataFieldsDataElements.from_dict(_data_elements)

        metadata_fields = cls(
            fields=fields,
            data_elements=data_elements,
        )

        return metadata_fields
