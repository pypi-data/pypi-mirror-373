from enum import Enum


class SystemConfigurationDatastoresPluginType(str, Enum):
    PLUGIN = "plugin"

    def __str__(self) -> str:
        return str(self.value)
