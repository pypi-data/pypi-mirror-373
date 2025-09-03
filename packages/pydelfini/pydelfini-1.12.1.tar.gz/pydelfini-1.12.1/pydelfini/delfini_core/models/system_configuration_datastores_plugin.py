from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cache_file import CacheFile
from ..models.cache_mem import CacheMem
from ..models.system_configuration_datastores_plugin_options import (
    SystemConfigurationDatastoresPluginOptions,
)
from ..models.system_configuration_datastores_plugin_type import (
    SystemConfigurationDatastoresPluginType,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SystemConfigurationDatastoresPlugin")


@_attrs_define
class SystemConfigurationDatastoresPlugin:
    """SystemConfigurationDatastoresPlugin model

    Attributes:
        plugin_name (str):
        cache (Union['CacheFile', 'CacheMem', Unset]):
        enabled (Union[Unset, bool]):  Default: True.
        is_default (Union[Unset, bool]):  Default: False.
        options (Union[Unset, SystemConfigurationDatastoresPluginOptions]):
        type (Union[Unset, SystemConfigurationDatastoresPluginType]):
    """

    plugin_name: str
    cache: Union["CacheFile", "CacheMem", Unset] = UNSET
    enabled: Union[Unset, bool] = True
    is_default: Union[Unset, bool] = False
    options: Union[Unset, "SystemConfigurationDatastoresPluginOptions"] = UNSET
    type: Union[Unset, SystemConfigurationDatastoresPluginType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        plugin_name = self.plugin_name
        cache: Union[Dict[str, Any], Unset]
        if isinstance(self.cache, Unset):
            cache = UNSET
        elif isinstance(self.cache, CacheMem):
            cache = self.cache.to_dict()
        else:
            cache = self.cache.to_dict()

        enabled = self.enabled
        is_default = self.is_default
        options: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "plugin_name": plugin_name,
            }
        )
        if cache is not UNSET:
            field_dict["cache"] = cache
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if is_default is not UNSET:
            field_dict["is_default"] = is_default
        if options is not UNSET:
            field_dict["options"] = options
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationDatastoresPlugin` from a dict"""
        d = src_dict.copy()
        plugin_name = d.pop("plugin_name")

        def _parse_cache(data: object) -> Union["CacheFile", "CacheMem", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasconfig_datastore_cache_type_0 = CacheMem.from_dict(
                    data
                )

                return componentsschemasconfig_datastore_cache_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemasconfig_datastore_cache_type_1 = CacheFile.from_dict(data)

            return componentsschemasconfig_datastore_cache_type_1

        cache = _parse_cache(d.pop("cache", UNSET))

        enabled = d.pop("enabled", UNSET)

        is_default = d.pop("is_default", UNSET)

        _options = d.pop("options", UNSET)
        options: Union[Unset, SystemConfigurationDatastoresPluginOptions]
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = SystemConfigurationDatastoresPluginOptions.from_dict(_options)

        _type = d.pop("type", UNSET)
        type: Union[Unset, SystemConfigurationDatastoresPluginType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = SystemConfigurationDatastoresPluginType(_type)

        system_configuration_datastores_plugin = cls(
            plugin_name=plugin_name,
            cache=cache,
            enabled=enabled,
            is_default=is_default,
            options=options,
            type=type,
        )

        system_configuration_datastores_plugin.additional_properties = d
        return system_configuration_datastores_plugin

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
