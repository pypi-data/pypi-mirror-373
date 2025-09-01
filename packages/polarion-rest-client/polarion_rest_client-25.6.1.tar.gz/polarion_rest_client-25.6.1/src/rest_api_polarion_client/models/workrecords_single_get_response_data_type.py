from enum import Enum


class WorkrecordsSingleGetResponseDataType(str, Enum):
    WORKRECORDS = "workrecords"

    def __str__(self) -> str:
        return str(self.value)
