from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.metric_event import MetricEvent


T = TypeVar("T", bound="MetricEventList")


@_attrs_define
class MetricEventList:
    """MetricEventList model

    Attributes:
        events (List['MetricEvent']):
    """

    events: List["MetricEvent"]

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
        """Create an instance of :py:class:`MetricEventList` from a dict"""
        d = src_dict.copy()
        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = MetricEvent.from_dict(events_item_data)

            events.append(events_item)

        metric_event_list = cls(
            events=events,
        )

        return metric_event_list
