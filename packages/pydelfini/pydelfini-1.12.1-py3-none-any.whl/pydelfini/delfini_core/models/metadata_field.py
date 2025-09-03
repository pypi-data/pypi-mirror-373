from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="MetadataField")


@_attrs_define
class MetadataField:
    """MetadataField model

    Attributes:
        name (str):
        data_element_ref (Union[Unset, str]):
        is_array (Union[Unset, bool]):  Default: False.
        label (Union[Unset, str]):
    """

    name: str
    data_element_ref: Union[Unset, str] = UNSET
    is_array: Union[Unset, bool] = False
    label: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        name = self.name
        data_element_ref = self.data_element_ref
        is_array = self.is_array
        label = self.label

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
            }
        )
        if data_element_ref is not UNSET:
            field_dict["data_element_ref"] = data_element_ref
        if is_array is not UNSET:
            field_dict["is_array"] = is_array
        if label is not UNSET:
            field_dict["label"] = label

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetadataField` from a dict"""
        d = src_dict.copy()
        name = d.pop("name")

        data_element_ref = d.pop("data_element_ref", UNSET)

        is_array = d.pop("is_array", UNSET)

        label = d.pop("label", UNSET)

        metadata_field = cls(
            name=name,
            data_element_ref=data_element_ref,
            is_array=is_array,
            label=label,
        )

        return metadata_field
