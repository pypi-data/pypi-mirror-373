from enum import Enum


class ColumnSchemaType(str, Enum):
    BINARY = "Binary"
    BOOLEAN = "Boolean"
    CATEGORICAL = "Categorical"
    DATE = "Date"
    DATETIME = "Datetime"
    DECIMAL = "Decimal"
    DURATION = "Duration"
    FLOAT = "Float"
    INTEGER = "Integer"
    NULL = "Null"
    STRING = "String"
    TIME = "Time"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
