from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.tasks_schedules_schedules_item import TasksSchedulesSchedulesItem


T = TypeVar("T", bound="TasksSchedules")


@_attrs_define
class TasksSchedules:
    """TasksSchedules model

    Attributes:
        schedules (List['TasksSchedulesSchedulesItem']):
    """

    schedules: List["TasksSchedulesSchedulesItem"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        schedules = []
        for schedules_item_data in self.schedules:
            schedules_item = schedules_item_data.to_dict()
            schedules.append(schedules_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "schedules": schedules,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TasksSchedules` from a dict"""
        d = src_dict.copy()
        schedules = []
        _schedules = d.pop("schedules")
        for schedules_item_data in _schedules:
            schedules_item = TasksSchedulesSchedulesItem.from_dict(schedules_item_data)

            schedules.append(schedules_item)

        tasks_schedules = cls(
            schedules=schedules,
        )

        return tasks_schedules
