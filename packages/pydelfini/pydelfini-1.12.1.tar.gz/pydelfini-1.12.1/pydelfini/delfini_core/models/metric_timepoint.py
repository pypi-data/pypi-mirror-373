import datetime
from typing import Any
from typing import cast
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.metric_timepoint_partitions import MetricTimepointPartitions
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="MetricTimepoint")


@_attrs_define
class MetricTimepoint:
    """MetricTimepoint model

    Attributes:
        dt (datetime.datetime):
        value (Union[float, int]):
        partitions (Union[Unset, MetricTimepointPartitions]):
    """

    dt: datetime.datetime
    value: Union[float, int]
    partitions: Union[Unset, "MetricTimepointPartitions"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        dt = self.dt.isoformat()
        value: Union[float, int]
        value = self.value
        partitions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.partitions, Unset):
            partitions = self.partitions.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dt": dt,
                "value": value,
            }
        )
        if partitions is not UNSET:
            field_dict["partitions"] = partitions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetricTimepoint` from a dict"""
        d = src_dict.copy()
        dt = isoparse(d.pop("dt"))

        def _parse_value(data: object) -> Union[float, int]:
            return cast(Union[float, int], data)

        value = _parse_value(d.pop("value"))

        _partitions = d.pop("partitions", UNSET)
        partitions: Union[Unset, MetricTimepointPartitions]
        if isinstance(_partitions, Unset):
            partitions = UNSET
        else:
            partitions = MetricTimepointPartitions.from_dict(_partitions)

        metric_timepoint = cls(
            dt=dt,
            value=value,
            partitions=partitions,
        )

        return metric_timepoint
