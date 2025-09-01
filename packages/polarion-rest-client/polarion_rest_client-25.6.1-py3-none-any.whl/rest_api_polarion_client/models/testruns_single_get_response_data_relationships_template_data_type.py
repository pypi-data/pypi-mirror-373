from enum import Enum


class TestrunsSingleGetResponseDataRelationshipsTemplateDataType(str, Enum):
    TESTRUNS = "testruns"

    def __str__(self) -> str:
        return str(self.value)
