from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="TaskResultErrorsItem")


@_attrs_define
class TaskResultErrorsItem:
    """TaskResultErrorsItem model

    Attributes:
        exception (str):
        message (str):
        traceback (Union[Unset, str]):
    """

    exception: str
    message: str
    traceback: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        exception = self.exception
        message = self.message
        traceback = self.traceback

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "exception": exception,
                "message": message,
            }
        )
        if traceback is not UNSET:
            field_dict["traceback"] = traceback

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TaskResultErrorsItem` from a dict"""
        d = src_dict.copy()
        exception = d.pop("exception")

        message = d.pop("message")

        traceback = d.pop("traceback", UNSET)

        task_result_errors_item = cls(
            exception=exception,
            message=message,
            traceback=traceback,
        )

        task_result_errors_item.additional_properties = d
        return task_result_errors_item

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
