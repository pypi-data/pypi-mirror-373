from enum import Enum


class TestrecordsListPostRequestDataItemType(str, Enum):
    TESTRECORDS = "testrecords"

    def __str__(self) -> str:
        return str(self.value)
