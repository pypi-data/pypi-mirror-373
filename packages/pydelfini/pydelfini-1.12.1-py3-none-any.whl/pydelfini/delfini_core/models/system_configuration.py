from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.system_configuration_authentication import (
    SystemConfigurationAuthentication,
)
from ..models.system_configuration_cache import SystemConfigurationCache
from ..models.system_configuration_datastores import SystemConfigurationDatastores
from ..models.system_configuration_plugins import SystemConfigurationPlugins
from ..models.system_configuration_sessions import SystemConfigurationSessions
from ..models.system_configuration_workers import SystemConfigurationWorkers


T = TypeVar("T", bound="SystemConfiguration")


@_attrs_define
class SystemConfiguration:
    """SystemConfiguration model

    Attributes:
        authentication (SystemConfigurationAuthentication):
        cache (SystemConfigurationCache):
        datastores (SystemConfigurationDatastores):
        plugins (SystemConfigurationPlugins):
        sessions (SystemConfigurationSessions):
        workers (SystemConfigurationWorkers):
    """

    authentication: "SystemConfigurationAuthentication"
    cache: "SystemConfigurationCache"
    datastores: "SystemConfigurationDatastores"
    plugins: "SystemConfigurationPlugins"
    sessions: "SystemConfigurationSessions"
    workers: "SystemConfigurationWorkers"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        authentication = self.authentication.to_dict()
        cache = self.cache.to_dict()
        datastores = self.datastores.to_dict()
        plugins = self.plugins.to_dict()
        sessions = self.sessions.to_dict()
        workers = self.workers.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "authentication": authentication,
                "cache": cache,
                "datastores": datastores,
                "plugins": plugins,
                "sessions": sessions,
                "workers": workers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfiguration` from a dict"""
        d = src_dict.copy()
        authentication = SystemConfigurationAuthentication.from_dict(
            d.pop("authentication")
        )

        cache = SystemConfigurationCache.from_dict(d.pop("cache"))

        datastores = SystemConfigurationDatastores.from_dict(d.pop("datastores"))

        plugins = SystemConfigurationPlugins.from_dict(d.pop("plugins"))

        sessions = SystemConfigurationSessions.from_dict(d.pop("sessions"))

        workers = SystemConfigurationWorkers.from_dict(d.pop("workers"))

        system_configuration = cls(
            authentication=authentication,
            cache=cache,
            datastores=datastores,
            plugins=plugins,
            sessions=sessions,
            workers=workers,
        )

        return system_configuration
