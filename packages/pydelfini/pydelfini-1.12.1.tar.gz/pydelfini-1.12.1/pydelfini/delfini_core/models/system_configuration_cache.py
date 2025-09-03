from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_cache_cache_type import (
    SystemConfigurationCacheCacheType,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SystemConfigurationCache")


@_attrs_define
class SystemConfigurationCache:
    """SystemConfigurationCache model

    Attributes:
        cache_default_timeout (Union[Unset, int]):  Default: 300.
        cache_type (Union[Unset, SystemConfigurationCacheCacheType]):
    """

    cache_default_timeout: Union[Unset, int] = 300
    cache_type: Union[Unset, SystemConfigurationCacheCacheType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        cache_default_timeout = self.cache_default_timeout
        cache_type: Union[Unset, str] = UNSET
        if not isinstance(self.cache_type, Unset):
            cache_type = self.cache_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cache_default_timeout is not UNSET:
            field_dict["cache_default_timeout"] = cache_default_timeout
        if cache_type is not UNSET:
            field_dict["cache_type"] = cache_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationCache` from a dict"""
        d = src_dict.copy()
        cache_default_timeout = d.pop("cache_default_timeout", UNSET)

        _cache_type = d.pop("cache_type", UNSET)
        cache_type: Union[Unset, SystemConfigurationCacheCacheType]
        if isinstance(_cache_type, Unset):
            cache_type = UNSET
        else:
            cache_type = SystemConfigurationCacheCacheType(_cache_type)

        system_configuration_cache = cls(
            cache_default_timeout=cache_default_timeout,
            cache_type=cache_type,
        )

        system_configuration_cache.additional_properties = d
        return system_configuration_cache

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
