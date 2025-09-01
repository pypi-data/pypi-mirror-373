from enum import Enum


class WorkitemsListGetResponseDataItemRelationshipsTestStepsDataItemType(str, Enum):
    TESTSTEPS = "teststeps"

    def __str__(self) -> str:
        return str(self.value)
