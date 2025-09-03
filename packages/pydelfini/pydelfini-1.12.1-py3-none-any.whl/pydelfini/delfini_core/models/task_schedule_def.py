from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.task_def import TaskDef
from ..models.task_schedule_def_frequency import TaskScheduleDefFrequency
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="TaskScheduleDef")


@_attrs_define
class TaskScheduleDef:
    """TaskScheduleDef model

    Attributes:
        name (str):
        task (TaskDef):
        cronspec (Union[None, Unset, str]):
        frequency (Union[None, TaskScheduleDefFrequency, Unset]):
    """

    name: str
    task: "TaskDef"
    cronspec: Union[None, Unset, str] = UNSET
    frequency: Union[None, TaskScheduleDefFrequency, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        name = self.name
        task = self.task.to_dict()
        cronspec: Union[None, Unset, str]
        if isinstance(self.cronspec, Unset):
            cronspec = UNSET
        else:
            cronspec = self.cronspec
        frequency: Union[None, Unset, str]
        if isinstance(self.frequency, Unset):
            frequency = UNSET
        elif isinstance(self.frequency, TaskScheduleDefFrequency):
            frequency = self.frequency.value
        else:
            frequency = self.frequency

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "task": task,
            }
        )
        if cronspec is not UNSET:
            field_dict["cronspec"] = cronspec
        if frequency is not UNSET:
            field_dict["frequency"] = frequency

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TaskScheduleDef` from a dict"""
        d = src_dict.copy()
        name = d.pop("name")

        task = TaskDef.from_dict(d.pop("task"))

        def _parse_cronspec(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        cronspec = _parse_cronspec(d.pop("cronspec", UNSET))

        def _parse_frequency(
            data: object,
        ) -> Union[None, TaskScheduleDefFrequency, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                frequency_type_0 = TaskScheduleDefFrequency(data)

                return frequency_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, TaskScheduleDefFrequency, Unset], data)

        frequency = _parse_frequency(d.pop("frequency", UNSET))

        task_schedule_def = cls(
            name=name,
            task=task,
            cronspec=cronspec,
            frequency=frequency,
        )

        task_schedule_def.additional_properties = d
        return task_schedule_def

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
