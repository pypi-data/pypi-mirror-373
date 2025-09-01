from enum import Enum


class TestparametersSingleGetResponseDataType(str, Enum):
    TESTPARAMETERS = "testparameters"

    def __str__(self) -> str:
        return str(self.value)
