from enum import Enum


class TestrecordsListPostResponseDataItemType(str, Enum):
    TESTRECORDS = "testrecords"

    def __str__(self) -> str:
        return str(self.value)
