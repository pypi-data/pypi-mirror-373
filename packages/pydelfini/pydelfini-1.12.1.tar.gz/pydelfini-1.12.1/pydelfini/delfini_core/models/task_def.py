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

from ..models.task_def_data_type_4 import TaskDefDataType4
from ..models.task_def_retry_item import TaskDefRetryItem
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="TaskDef")


@_attrs_define
class TaskDef:
    """TaskDef model

    Attributes:
        action (str):
        deadline (Union[datetime.datetime, float]):
        retry (List['TaskDefRetryItem']):
        data (Union['TaskDefDataType4', List[Any], Unset, float, int, str]):
        id (Union[Unset, str]):
        idemkey (Union[Unset, str]):
        priority (Union[Unset, int]):  Default: 0.
    """

    action: str
    deadline: Union[datetime.datetime, float]
    retry: List["TaskDefRetryItem"]
    data: Union["TaskDefDataType4", List[Any], Unset, float, int, str] = UNSET
    id: Union[Unset, str] = UNSET
    idemkey: Union[Unset, str] = UNSET
    priority: Union[Unset, int] = 0
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        action = self.action
        deadline: Union[float, str]
        if isinstance(self.deadline, datetime.datetime):
            deadline = self.deadline.isoformat()
        else:
            deadline = self.deadline
        retry = []
        for retry_item_data in self.retry:
            retry_item = retry_item_data.to_dict()
            retry.append(retry_item)

        data: Union[Dict[str, Any], List[Any], Unset, float, int, str]
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, list):
            data = self.data

        elif isinstance(self.data, TaskDefDataType4):
            data = self.data.to_dict()
        else:
            data = self.data
        id = self.id
        idemkey = self.idemkey
        priority = self.priority

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
                "deadline": deadline,
                "retry": retry,
            }
        )
        if data is not UNSET:
            field_dict["data"] = data
        if id is not UNSET:
            field_dict["id"] = id
        if idemkey is not UNSET:
            field_dict["idemkey"] = idemkey
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TaskDef` from a dict"""
        d = src_dict.copy()
        action = d.pop("action")

        def _parse_deadline(data: object) -> Union[datetime.datetime, float]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deadline_type_0 = isoparse(data)

                return deadline_type_0
            except:  # noqa: E722
                pass
            return cast(Union[datetime.datetime, float], data)

        deadline = _parse_deadline(d.pop("deadline"))

        retry = []
        _retry = d.pop("retry")
        for retry_item_data in _retry:
            retry_item = TaskDefRetryItem.from_dict(retry_item_data)

            retry.append(retry_item)

        def _parse_data(
            data: object,
        ) -> Union["TaskDefDataType4", List[Any], Unset, float, int, str]:
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
                data_type_4 = TaskDefDataType4.from_dict(data)

                return data_type_4
            except:  # noqa: E722
                pass
            return cast(
                Union["TaskDefDataType4", List[Any], Unset, float, int, str], data
            )

        data = _parse_data(d.pop("data", UNSET))

        id = d.pop("id", UNSET)

        idemkey = d.pop("idemkey", UNSET)

        priority = d.pop("priority", UNSET)

        task_def = cls(
            action=action,
            deadline=deadline,
            retry=retry,
            data=data,
            id=id,
            idemkey=idemkey,
            priority=priority,
        )

        task_def.additional_properties = d
        return task_def

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
