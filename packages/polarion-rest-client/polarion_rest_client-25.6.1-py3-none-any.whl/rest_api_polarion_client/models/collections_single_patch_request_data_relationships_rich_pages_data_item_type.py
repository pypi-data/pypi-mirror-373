from enum import Enum


class CollectionsSinglePatchRequestDataRelationshipsRichPagesDataItemType(str, Enum):
    PAGES = "pages"

    def __str__(self) -> str:
        return str(self.value)
