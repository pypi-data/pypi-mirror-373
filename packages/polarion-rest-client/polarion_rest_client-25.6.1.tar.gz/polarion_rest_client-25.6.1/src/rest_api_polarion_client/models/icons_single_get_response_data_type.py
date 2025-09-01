from enum import Enum


class IconsSingleGetResponseDataType(str, Enum):
    ICONS = "icons"

    def __str__(self) -> str:
        return str(self.value)
