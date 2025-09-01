from enum import Enum


class CollectionsSingleGetResponseDataRelationshipsRichPagesDataItemType(str, Enum):
    PAGES = "pages"

    def __str__(self) -> str:
        return str(self.value)
