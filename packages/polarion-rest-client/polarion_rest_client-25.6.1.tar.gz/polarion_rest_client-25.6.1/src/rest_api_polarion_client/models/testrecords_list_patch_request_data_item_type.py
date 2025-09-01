from enum import Enum


class TestrecordsListPatchRequestDataItemType(str, Enum):
    TESTRECORDS = "testrecords"

    def __str__(self) -> str:
        return str(self.value)
