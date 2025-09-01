from enum import Enum


class TestrecordsListGetResponseDataItemRelationshipsTestCaseDataType(str, Enum):
    WORKITEMS = "workitems"

    def __str__(self) -> str:
        return str(self.value)
