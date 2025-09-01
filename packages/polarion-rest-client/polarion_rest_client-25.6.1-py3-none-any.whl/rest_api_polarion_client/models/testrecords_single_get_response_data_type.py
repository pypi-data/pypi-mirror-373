from enum import Enum


class TestrecordsSingleGetResponseDataType(str, Enum):
    TESTRECORDS = "testrecords"

    def __str__(self) -> str:
        return str(self.value)
