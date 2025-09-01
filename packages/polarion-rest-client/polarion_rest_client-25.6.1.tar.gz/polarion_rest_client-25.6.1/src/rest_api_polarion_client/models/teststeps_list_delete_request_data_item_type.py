from enum import Enum


class TeststepsListDeleteRequestDataItemType(str, Enum):
    TESTSTEPS = "teststeps"

    def __str__(self) -> str:
        return str(self.value)
