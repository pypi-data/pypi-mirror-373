from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.metric_log_entry import MetricLogEntry


T = TypeVar("T", bound="MetricLog")


@_attrs_define
class MetricLog:
    """MetricLog model

    Attributes:
        events (List['MetricLogEntry']):
    """

    events: List["MetricLogEntry"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        events = []
        for events_item_data in self.events:
            events_item = events_item_data.to_dict()
            events.append(events_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "events": events,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetricLog` from a dict"""
        d = src_dict.copy()
        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = MetricLogEntry.from_dict(events_item_data)

            events.append(events_item)

        metric_log = cls(
            events=events,
        )

        return metric_log
