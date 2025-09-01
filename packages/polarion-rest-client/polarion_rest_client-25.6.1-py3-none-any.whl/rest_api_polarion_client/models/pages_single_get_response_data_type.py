from enum import Enum


class PagesSingleGetResponseDataType(str, Enum):
    PAGES = "pages"

    def __str__(self) -> str:
        return str(self.value)
