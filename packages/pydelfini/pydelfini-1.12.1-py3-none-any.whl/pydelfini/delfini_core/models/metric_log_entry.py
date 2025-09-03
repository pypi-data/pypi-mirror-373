import datetime
from typing import Any
from typing import cast
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.metric_log_entry_dimensions import MetricLogEntryDimensions


T = TypeVar("T", bound="MetricLogEntry")


@_attrs_define
class MetricLogEntry:
    """MetricLogEntry model

    Attributes:
        dimensions (MetricLogEntryDimensions):
        dt (datetime.datetime):
        name (str):
        value (Union[float, int]):
    """

    dimensions: "MetricLogEntryDimensions"
    dt: datetime.datetime
    name: str
    value: Union[float, int]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        dimensions = self.dimensions.to_dict()
        dt = self.dt.isoformat()
        name = self.name
        value: Union[float, int]
        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dimensions": dimensions,
                "dt": dt,
                "name": name,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetricLogEntry` from a dict"""
        d = src_dict.copy()
        dimensions = MetricLogEntryDimensions.from_dict(d.pop("dimensions"))

        dt = isoparse(d.pop("dt"))

        name = d.pop("name")

        def _parse_value(data: object) -> Union[float, int]:
            return cast(Union[float, int], data)

        value = _parse_value(d.pop("value"))

        metric_log_entry = cls(
            dimensions=dimensions,
            dt=dt,
            name=name,
            value=value,
        )

        return metric_log_entry
