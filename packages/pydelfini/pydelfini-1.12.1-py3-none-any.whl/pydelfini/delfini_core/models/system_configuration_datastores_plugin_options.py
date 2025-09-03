from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field


T = TypeVar("T", bound="SystemConfigurationDatastoresPluginOptions")


@_attrs_define
class SystemConfigurationDatastoresPluginOptions:
    """SystemConfigurationDatastoresPluginOptions model"""

    additional_properties: Dict[str, Union[bool, float, int, str]] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationDatastoresPluginOptions` from a dict"""
        d = src_dict.copy()
        system_configuration_datastores_plugin_options = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(
                data: object,
            ) -> Union[bool, float, int, str]:
                return cast(Union[bool, float, int, str], data)

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        system_configuration_datastores_plugin_options.additional_properties = (
            additional_properties
        )
        return system_configuration_datastores_plugin_options

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Union[bool, float, int, str]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Union[bool, float, int, str]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
