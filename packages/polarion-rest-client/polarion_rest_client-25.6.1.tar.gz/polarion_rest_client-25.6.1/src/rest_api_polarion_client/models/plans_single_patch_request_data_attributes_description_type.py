from enum import Enum


class PlansSinglePatchRequestDataAttributesDescriptionType(str, Enum):
    TEXTPLAIN = "text/plain"

    def __str__(self) -> str:
        return str(self.value)
