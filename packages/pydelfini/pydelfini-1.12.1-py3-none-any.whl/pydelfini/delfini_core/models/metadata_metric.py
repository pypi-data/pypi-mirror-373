from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.metadata_metric_type import MetadataMetricType
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="MetadataMetric")


@_attrs_define
class MetadataMetric:
    """MetadataMetric model

    Attributes:
        description (str):
        name (str):
        type (Union[Unset, MetadataMetricType]):  Default: MetadataMetricType.METADATA.
    """

    description: str
    name: str
    type: Union[Unset, MetadataMetricType] = MetadataMetricType.METADATA

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        description = self.description
        name = self.name
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "description": description,
                "name": name,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetadataMetric` from a dict"""
        d = src_dict.copy()
        description = d.pop("description")

        name = d.pop("name")

        _type = d.pop("type", UNSET)
        type: Union[Unset, MetadataMetricType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = MetadataMetricType(_type)

        metadata_metric = cls(
            description=description,
            name=name,
            type=type,
        )

        return metadata_metric
