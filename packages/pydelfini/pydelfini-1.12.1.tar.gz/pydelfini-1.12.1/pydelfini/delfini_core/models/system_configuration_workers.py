from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_workers_backend_type import (
    SystemConfigurationWorkersBackendType,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SystemConfigurationWorkers")


@_attrs_define
class SystemConfigurationWorkers:
    """SystemConfigurationWorkers model

    Attributes:
        backend_connection (Union[Unset, str]):
        backend_cycle_time (Union[Unset, float]):  Default: 15.0.
        backend_type (Union[Unset, SystemConfigurationWorkersBackendType]):
        num_worker_threads (Union[Unset, int]):  Default: 2.
    """

    backend_connection: Union[Unset, str] = UNSET
    backend_cycle_time: Union[Unset, float] = 15.0
    backend_type: Union[Unset, SystemConfigurationWorkersBackendType] = UNSET
    num_worker_threads: Union[Unset, int] = 2
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        backend_connection = self.backend_connection
        backend_cycle_time = self.backend_cycle_time
        backend_type: Union[Unset, str] = UNSET
        if not isinstance(self.backend_type, Unset):
            backend_type = self.backend_type.value

        num_worker_threads = self.num_worker_threads

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if backend_connection is not UNSET:
            field_dict["backend_connection"] = backend_connection
        if backend_cycle_time is not UNSET:
            field_dict["backend_cycle_time"] = backend_cycle_time
        if backend_type is not UNSET:
            field_dict["backend_type"] = backend_type
        if num_worker_threads is not UNSET:
            field_dict["num_worker_threads"] = num_worker_threads

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationWorkers` from a dict"""
        d = src_dict.copy()
        backend_connection = d.pop("backend_connection", UNSET)

        backend_cycle_time = d.pop("backend_cycle_time", UNSET)

        _backend_type = d.pop("backend_type", UNSET)
        backend_type: Union[Unset, SystemConfigurationWorkersBackendType]
        if isinstance(_backend_type, Unset):
            backend_type = UNSET
        else:
            backend_type = SystemConfigurationWorkersBackendType(_backend_type)

        num_worker_threads = d.pop("num_worker_threads", UNSET)

        system_configuration_workers = cls(
            backend_connection=backend_connection,
            backend_cycle_time=backend_cycle_time,
            backend_type=backend_type,
            num_worker_threads=num_worker_threads,
        )

        system_configuration_workers.additional_properties = d
        return system_configuration_workers

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
