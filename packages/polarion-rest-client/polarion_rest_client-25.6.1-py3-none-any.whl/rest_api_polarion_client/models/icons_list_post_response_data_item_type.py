from enum import Enum


class IconsListPostResponseDataItemType(str, Enum):
    ICONS = "icons"

    def __str__(self) -> str:
        return str(self.value)
