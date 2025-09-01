from enum import Enum


class TestrunsListPostRequestDataItemType(str, Enum):
    TESTRUNS = "testruns"

    def __str__(self) -> str:
        return str(self.value)
