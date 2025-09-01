from enum import Enum


class TestrunsSinglePatchRequestDataType(str, Enum):
    TESTRUNS = "testruns"

    def __str__(self) -> str:
        return str(self.value)
