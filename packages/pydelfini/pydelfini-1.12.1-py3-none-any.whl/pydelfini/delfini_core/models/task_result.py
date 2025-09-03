import datetime
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.task_result_data_type_4 import TaskResultDataType4
from ..models.task_result_errors_item import TaskResultErrorsItem
from ..models.task_result_status import TaskResultStatus
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="TaskResult")


@_attrs_define
class TaskResult:
    """TaskResult model

    Attributes:
        event_time (datetime.datetime):
        start_time (datetime.datetime):
        status (TaskResultStatus):
        task_id (str):
        task_idemkey (str):
        worker (str):
        data (Union['TaskResultDataType4', List[Any], Unset, float, int, str]):
        errors (Union[Unset, List['TaskResultErrorsItem']]):
        id (Union[Unset, str]):
    """

    event_time: datetime.datetime
    start_time: datetime.datetime
    status: TaskResultStatus
    task_id: str
    task_idemkey: str
    worker: str
    data: Union["TaskResultDataType4", List[Any], Unset, float, int, str] = UNSET
    errors: Union[Unset, List["TaskResultErrorsItem"]] = UNSET
    id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        event_time = self.event_time.isoformat()
        start_time = self.start_time.isoformat()
        status = self.status.value
        task_id = self.task_id
        task_idemkey = self.task_idemkey
        worker = self.worker
        data: Union[Dict[str, Any], List[Any], Unset, float, int, str]
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, list):
            data = self.data

        elif isinstance(self.data, TaskResultDataType4):
            data = self.data.to_dict()
        else:
            data = self.data
        errors: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for errors_item_data in self.errors:
                errors_item = errors_item_data.to_dict()
                errors.append(errors_item)

        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event_time": event_time,
                "start_time": start_time,
                "status": status,
                "task_id": task_id,
                "task_idemkey": task_idemkey,
                "worker": worker,
            }
        )
        if data is not UNSET:
            field_dict["data"] = data
        if errors is not UNSET:
            field_dict["errors"] = errors
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TaskResult` from a dict"""
        d = src_dict.copy()
        event_time = isoparse(d.pop("event_time"))

        start_time = isoparse(d.pop("start_time"))

        status = TaskResultStatus(d.pop("status"))

        task_id = d.pop("task_id")

        task_idemkey = d.pop("task_idemkey")

        worker = d.pop("worker")

        def _parse_data(
            data: object,
        ) -> Union["TaskResultDataType4", List[Any], Unset, float, int, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                data_type_3 = cast(List[Any], data)

                return data_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_4 = TaskResultDataType4.from_dict(data)

                return data_type_4
            except:  # noqa: E722
                pass
            return cast(
                Union["TaskResultDataType4", List[Any], Unset, float, int, str], data
            )

        data = _parse_data(d.pop("data", UNSET))

        errors = []
        _errors = d.pop("errors", UNSET)
        for errors_item_data in _errors or []:
            errors_item = TaskResultErrorsItem.from_dict(errors_item_data)

            errors.append(errors_item)

        id = d.pop("id", UNSET)

        task_result = cls(
            event_time=event_time,
            start_time=start_time,
            status=status,
            task_id=task_id,
            task_idemkey=task_idemkey,
            worker=worker,
            data=data,
            errors=errors,
            id=id,
        )

        task_result.additional_properties = d
        return task_result

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
