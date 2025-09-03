from enum import Enum


class DataElementConceptAppliesTo(str, Enum):
    CONCEPTUALDOMAIN = "conceptualDomain"
    DATAELEMENT = "dataElement"
    OBJECTCLASS = "objectClass"
    VALUEDOMAIN = "valueDomain"

    def __str__(self) -> str:
        return str(self.value)
