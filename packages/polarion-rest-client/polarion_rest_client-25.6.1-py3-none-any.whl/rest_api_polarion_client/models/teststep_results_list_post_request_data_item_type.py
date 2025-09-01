from enum import Enum


class TeststepResultsListPostRequestDataItemType(str, Enum):
    TESTSTEP_RESULTS = "teststep_results"

    def __str__(self) -> str:
        return str(self.value)
