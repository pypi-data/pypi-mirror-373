from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_datastores_local import (
    SystemConfigurationDatastoresLocal,
)
from ..models.system_configuration_datastores_plugin import (
    SystemConfigurationDatastoresPlugin,
)
from ..models.system_configuration_datastores_s3 import SystemConfigurationDatastoresS3


T = TypeVar("T", bound="SystemConfigurationDatastores")


@_attrs_define
class SystemConfigurationDatastores:
    """SystemConfigurationDatastores model"""

    additional_properties: Dict[
        str,
        Union[
            "SystemConfigurationDatastoresLocal",
            "SystemConfigurationDatastoresPlugin",
            "SystemConfigurationDatastoresS3",
        ],
    ] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, SystemConfigurationDatastoresLocal):
                field_dict[prop_name] = prop.to_dict()
            elif isinstance(prop, SystemConfigurationDatastoresS3):
                field_dict[prop_name] = prop.to_dict()
            else:
                field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationDatastores` from a dict"""
        d = src_dict.copy()
        system_configuration_datastores = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(
                data: object,
            ) -> Union[
                "SystemConfigurationDatastoresLocal",
                "SystemConfigurationDatastoresPlugin",
                "SystemConfigurationDatastoresS3",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_0 = (
                        SystemConfigurationDatastoresLocal.from_dict(data)
                    )

                    return additional_property_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_1 = (
                        SystemConfigurationDatastoresS3.from_dict(data)
                    )

                    return additional_property_type_1
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                additional_property_type_2 = (
                    SystemConfigurationDatastoresPlugin.from_dict(data)
                )

                return additional_property_type_2

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        system_configuration_datastores.additional_properties = additional_properties
        return system_configuration_datastores

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(
        self, key: str
    ) -> Union[
        "SystemConfigurationDatastoresLocal",
        "SystemConfigurationDatastoresPlugin",
        "SystemConfigurationDatastoresS3",
    ]:
        return self.additional_properties[key]

    def __setitem__(
        self,
        key: str,
        value: Union[
            "SystemConfigurationDatastoresLocal",
            "SystemConfigurationDatastoresPlugin",
            "SystemConfigurationDatastoresS3",
        ],
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
