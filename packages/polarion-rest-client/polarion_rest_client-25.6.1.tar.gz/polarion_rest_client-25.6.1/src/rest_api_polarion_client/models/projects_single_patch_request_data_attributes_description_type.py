from enum import Enum


class ProjectsSinglePatchRequestDataAttributesDescriptionType(str, Enum):
    TEXTPLAIN = "text/plain"

    def __str__(self) -> str:
        return str(self.value)
