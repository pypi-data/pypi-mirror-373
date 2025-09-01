from enum import Enum


class TestparametersListDeleteRequestDataItemType(str, Enum):
    TESTPARAMETERS = "testparameters"

    def __str__(self) -> str:
        return str(self.value)
