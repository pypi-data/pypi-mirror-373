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


T = TypeVar("T", bound="TaskDefRetryItem")


@_attrs_define
class TaskDefRetryItem:
    """TaskDefRetryItem model

    Attributes:
        cancel_after (Union[Unset, int]):  Default: 0.
        cancel_if (Union[Unset, str]):  Default: '$-'.
        fail_after (Union[Unset, int]):  Default: 0.
        fail_if (Union[Unset, str]):  Default: '$-'.
        max_retries (Union[Unset, int]):  Default: 1.
        priority_delta (Union[Unset, int]):  Default: 0.
        retry_after (Union[Unset, int]):  Default: 0.
        retry_if (Union[Unset, str]):  Default: '$-'.
    """

    cancel_after: Union[Unset, int] = 0
    cancel_if: Union[Unset, str] = "$-"
    fail_after: Union[Unset, int] = 0
    fail_if: Union[Unset, str] = "$-"
    max_retries: Union[Unset, int] = 1
    priority_delta: Union[Unset, int] = 0
    retry_after: Union[Unset, int] = 0
    retry_if: Union[Unset, str] = "$-"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        cancel_after = self.cancel_after
        cancel_if = self.cancel_if
        fail_after = self.fail_after
        fail_if = self.fail_if
        max_retries = self.max_retries
        priority_delta = self.priority_delta
        retry_after = self.retry_after
        retry_if = self.retry_if

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cancel_after is not UNSET:
            field_dict["cancel_after"] = cancel_after
        if cancel_if is not UNSET:
            field_dict["cancel_if"] = cancel_if
        if fail_after is not UNSET:
            field_dict["fail_after"] = fail_after
        if fail_if is not UNSET:
            field_dict["fail_if"] = fail_if
        if max_retries is not UNSET:
            field_dict["max_retries"] = max_retries
        if priority_delta is not UNSET:
            field_dict["priority_delta"] = priority_delta
        if retry_after is not UNSET:
            field_dict["retry_after"] = retry_after
        if retry_if is not UNSET:
            field_dict["retry_if"] = retry_if

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TaskDefRetryItem` from a dict"""
        d = src_dict.copy()
        cancel_after = d.pop("cancel_after", UNSET)

        cancel_if = d.pop("cancel_if", UNSET)

        fail_after = d.pop("fail_after", UNSET)

        fail_if = d.pop("fail_if", UNSET)

        max_retries = d.pop("max_retries", UNSET)

        priority_delta = d.pop("priority_delta", UNSET)

        retry_after = d.pop("retry_after", UNSET)

        retry_if = d.pop("retry_if", UNSET)

        task_def_retry_item = cls(
            cancel_after=cancel_after,
            cancel_if=cancel_if,
            fail_after=fail_after,
            fail_if=fail_if,
            max_retries=max_retries,
            priority_delta=priority_delta,
            retry_after=retry_after,
            retry_if=retry_if,
        )

        task_def_retry_item.additional_properties = d
        return task_def_retry_item

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
