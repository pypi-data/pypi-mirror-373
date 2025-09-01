from enum import Enum


class WorkrecordsListPostResponseDataItemType(str, Enum):
    WORKRECORDS = "workrecords"

    def __str__(self) -> str:
        return str(self.value)
