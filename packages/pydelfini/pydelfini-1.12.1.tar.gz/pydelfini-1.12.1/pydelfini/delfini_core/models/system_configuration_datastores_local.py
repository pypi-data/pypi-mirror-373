from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_datastores_local_type import (
    SystemConfigurationDatastoresLocalType,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SystemConfigurationDatastoresLocal")


@_attrs_define
class SystemConfigurationDatastoresLocal:
    """SystemConfigurationDatastoresLocal model

    Attributes:
        enabled (Union[Unset, bool]):  Default: True.
        is_default (Union[Unset, bool]):  Default: False.
        path (Union[Unset, str]):
        type (Union[Unset, SystemConfigurationDatastoresLocalType]):
    """

    enabled: Union[Unset, bool] = True
    is_default: Union[Unset, bool] = False
    path: Union[Unset, str] = UNSET
    type: Union[Unset, SystemConfigurationDatastoresLocalType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        enabled = self.enabled
        is_default = self.is_default
        path = self.path
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if is_default is not UNSET:
            field_dict["is_default"] = is_default
        if path is not UNSET:
            field_dict["path"] = path
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationDatastoresLocal` from a dict"""
        d = src_dict.copy()
        enabled = d.pop("enabled", UNSET)

        is_default = d.pop("is_default", UNSET)

        path = d.pop("path", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, SystemConfigurationDatastoresLocalType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = SystemConfigurationDatastoresLocalType(_type)

        system_configuration_datastores_local = cls(
            enabled=enabled,
            is_default=is_default,
            path=path,
            type=type,
        )

        system_configuration_datastores_local.additional_properties = d
        return system_configuration_datastores_local

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
