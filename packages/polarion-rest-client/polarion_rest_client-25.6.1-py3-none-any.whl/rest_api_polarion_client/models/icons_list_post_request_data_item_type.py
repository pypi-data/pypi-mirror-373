from enum import Enum


class IconsListPostRequestDataItemType(str, Enum):
    ICONS = "icons"

    def __str__(self) -> str:
        return str(self.value)
