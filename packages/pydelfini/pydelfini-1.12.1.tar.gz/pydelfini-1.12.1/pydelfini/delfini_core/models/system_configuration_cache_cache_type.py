from enum import Enum


class SystemConfigurationCacheCacheType(str, Enum):
    SIMPLECACHE = "SimpleCache"

    def __str__(self) -> str:
        return str(self.value)
