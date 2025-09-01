from enum import Enum


class CollectionsListGetResponseDataItemRelationshipsRichPagesDataItemType(str, Enum):
    PAGES = "pages"

    def __str__(self) -> str:
        return str(self.value)
