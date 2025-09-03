from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.metric_timepoint import MetricTimepoint


T = TypeVar("T", bound="MetricData")


@_attrs_define
class MetricData:
    """MetricData model

    Attributes:
        data (List['MetricTimepoint']):
    """

    data: List["MetricTimepoint"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetricData` from a dict"""
        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = MetricTimepoint.from_dict(data_item_data)

            data.append(data_item)

        metric_data = cls(
            data=data,
        )

        return metric_data
