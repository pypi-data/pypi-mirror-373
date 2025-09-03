from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="TasksStats")


@_attrs_define
class TasksStats:
    """TasksStats model

    Attributes:
        queued (int):
        results (int):
        schedules (int):
    """

    queued: int
    results: int
    schedules: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        queued = self.queued
        results = self.results
        schedules = self.schedules

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "queued": queued,
                "results": results,
                "schedules": schedules,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TasksStats` from a dict"""
        d = src_dict.copy()
        queued = d.pop("queued")

        results = d.pop("results")

        schedules = d.pop("schedules")

        tasks_stats = cls(
            queued=queued,
            results=results,
            schedules=schedules,
        )

        return tasks_stats
