from enum import Enum


class DataElementPermissibleValuesDateTimeFormatDateTimeFormatFormatType0Isoformat(
    str, Enum
):
    DATE = "date"
    DATE_TIME = "date-time"
    DURATION = "duration"
    TIME = "time"

    def __str__(self) -> str:
        return str(self.value)
