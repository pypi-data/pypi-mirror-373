from enum import Enum


class EnumerationsListPostRequestDataItemType(str, Enum):
    ENUMERATIONS = "enumerations"

    def __str__(self) -> str:
        return str(self.value)
