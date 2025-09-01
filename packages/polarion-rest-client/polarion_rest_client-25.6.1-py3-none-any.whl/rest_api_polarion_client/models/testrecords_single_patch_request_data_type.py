from enum import Enum


class TestrecordsSinglePatchRequestDataType(str, Enum):
    TESTRECORDS = "testrecords"

    def __str__(self) -> str:
        return str(self.value)
