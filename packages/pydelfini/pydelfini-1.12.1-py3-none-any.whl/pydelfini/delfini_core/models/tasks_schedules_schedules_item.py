import datetime
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.task_schedule_def import TaskScheduleDef


T = TypeVar("T", bound="TasksSchedulesSchedulesItem")


@_attrs_define
class TasksSchedulesSchedulesItem:
    """TasksSchedulesSchedulesItem model

    Attributes:
        definition (TaskScheduleDef):
        next_run_time (datetime.datetime):
    """

    definition: "TaskScheduleDef"
    next_run_time: datetime.datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        definition = self.definition.to_dict()
        next_run_time = self.next_run_time.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "definition": definition,
                "next_run_time": next_run_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TasksSchedulesSchedulesItem` from a dict"""
        d = src_dict.copy()
        definition = TaskScheduleDef.from_dict(d.pop("definition"))

        next_run_time = isoparse(d.pop("next_run_time"))

        tasks_schedules_schedules_item = cls(
            definition=definition,
            next_run_time=next_run_time,
        )

        return tasks_schedules_schedules_item
