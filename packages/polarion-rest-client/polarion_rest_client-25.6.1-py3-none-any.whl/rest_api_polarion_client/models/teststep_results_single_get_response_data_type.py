from enum import Enum


class TeststepResultsSingleGetResponseDataType(str, Enum):
    TESTSTEP_RESULTS = "teststep_results"

    def __str__(self) -> str:
        return str(self.value)
