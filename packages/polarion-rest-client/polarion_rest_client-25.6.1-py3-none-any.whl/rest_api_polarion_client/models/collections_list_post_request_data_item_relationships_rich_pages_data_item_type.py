from enum import Enum


class CollectionsListPostRequestDataItemRelationshipsRichPagesDataItemType(str, Enum):
    PAGES = "pages"

    def __str__(self) -> str:
        return str(self.value)
