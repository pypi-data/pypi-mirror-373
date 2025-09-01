from enum import Enum


class PlansListGetResponseDataItemAttributesDescriptionType(str, Enum):
    TEXTPLAIN = "text/plain"

    def __str__(self) -> str:
        return str(self.value)
