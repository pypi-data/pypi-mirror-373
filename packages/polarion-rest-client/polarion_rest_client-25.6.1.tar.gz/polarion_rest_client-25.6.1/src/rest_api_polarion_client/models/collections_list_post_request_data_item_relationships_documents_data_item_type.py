from enum import Enum


class CollectionsListPostRequestDataItemRelationshipsDocumentsDataItemType(str, Enum):
    DOCUMENTS = "documents"

    def __str__(self) -> str:
        return str(self.value)
