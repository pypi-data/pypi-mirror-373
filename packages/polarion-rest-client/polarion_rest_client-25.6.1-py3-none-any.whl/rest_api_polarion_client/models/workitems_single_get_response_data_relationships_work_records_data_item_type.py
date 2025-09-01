from enum import Enum


class WorkitemsSingleGetResponseDataRelationshipsWorkRecordsDataItemType(str, Enum):
    WORKRECORDS = "workrecords"

    def __str__(self) -> str:
        return str(self.value)
