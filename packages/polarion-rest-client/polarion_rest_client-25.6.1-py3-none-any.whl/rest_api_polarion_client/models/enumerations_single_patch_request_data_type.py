from enum import Enum


class EnumerationsSinglePatchRequestDataType(str, Enum):
    ENUMERATIONS = "enumerations"

    def __str__(self) -> str:
        return str(self.value)
