from enum import Enum


class TestrecordsSinglePatchRequestDataRelationshipsExecutedByDataType(str, Enum):
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
