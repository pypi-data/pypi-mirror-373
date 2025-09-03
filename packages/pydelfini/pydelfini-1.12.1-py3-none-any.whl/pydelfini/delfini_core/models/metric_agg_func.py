from enum import Enum


class MetricAggFunc(str, Enum):
    AVG = "avg"
    CARDINALITY = "cardinality"
    COUNT = "count"
    SUM = "sum"

    def __str__(self) -> str:
        return str(self.value)
