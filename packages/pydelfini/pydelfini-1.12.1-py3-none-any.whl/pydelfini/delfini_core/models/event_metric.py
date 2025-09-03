from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.event_metric_dimensions import EventMetricDimensions
from ..models.event_metric_type import EventMetricType
from ..models.metric_agg_func import MetricAggFunc
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="EventMetric")


@_attrs_define
class EventMetric:
    """EventMetric model

    Attributes:
        agg_func (MetricAggFunc):
        description (str):
        event_name (str):
        name (str):
        dimensions (Union[Unset, EventMetricDimensions]):
        num_partitions (Union[Unset, int]):
        partition_by (Union[Unset, str]):
        type (Union[Unset, EventMetricType]):  Default: EventMetricType.EVENT.
    """

    agg_func: MetricAggFunc
    description: str
    event_name: str
    name: str
    dimensions: Union[Unset, "EventMetricDimensions"] = UNSET
    num_partitions: Union[Unset, int] = UNSET
    partition_by: Union[Unset, str] = UNSET
    type: Union[Unset, EventMetricType] = EventMetricType.EVENT

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        agg_func = self.agg_func.value
        description = self.description
        event_name = self.event_name
        name = self.name
        dimensions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.dimensions, Unset):
            dimensions = self.dimensions.to_dict()
        num_partitions = self.num_partitions
        partition_by = self.partition_by
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "agg_func": agg_func,
                "description": description,
                "event_name": event_name,
                "name": name,
            }
        )
        if dimensions is not UNSET:
            field_dict["dimensions"] = dimensions
        if num_partitions is not UNSET:
            field_dict["num_partitions"] = num_partitions
        if partition_by is not UNSET:
            field_dict["partition_by"] = partition_by
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`EventMetric` from a dict"""
        d = src_dict.copy()
        agg_func = MetricAggFunc(d.pop("agg_func"))

        description = d.pop("description")

        event_name = d.pop("event_name")

        name = d.pop("name")

        _dimensions = d.pop("dimensions", UNSET)
        dimensions: Union[Unset, EventMetricDimensions]
        if isinstance(_dimensions, Unset):
            dimensions = UNSET
        else:
            dimensions = EventMetricDimensions.from_dict(_dimensions)

        num_partitions = d.pop("num_partitions", UNSET)

        partition_by = d.pop("partition_by", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, EventMetricType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = EventMetricType(_type)

        event_metric = cls(
            agg_func=agg_func,
            description=description,
            event_name=event_name,
            name=name,
            dimensions=dimensions,
            num_partitions=num_partitions,
            partition_by=partition_by,
            type=type,
        )

        return event_metric
