from enum import Enum


class TeststepResultsListGetResponseDataItemRelationshipsTestStepDataType(str, Enum):
    TESTSTEPS = "teststeps"

    def __str__(self) -> str:
        return str(self.value)
