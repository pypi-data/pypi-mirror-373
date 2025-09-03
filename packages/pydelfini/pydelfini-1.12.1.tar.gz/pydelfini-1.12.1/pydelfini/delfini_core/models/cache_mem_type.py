from enum import Enum


class CacheMemType(str, Enum):
    MEM = "mem"

    def __str__(self) -> str:
        return str(self.value)
