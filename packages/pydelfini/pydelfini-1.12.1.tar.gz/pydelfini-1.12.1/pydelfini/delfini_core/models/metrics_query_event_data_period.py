from enum import Enum


class MetricsQueryEventDataPeriod(str, Enum):
    VALUE_0 = "5-minutes"
    VALUE_1 = "15-minutes"
    VALUE_2 = "1-hour"
    VALUE_3 = "1-day"
    VALUE_4 = "1-week"
    VALUE_5 = "30-days"

    def __str__(self) -> str:
        return str(self.value)
