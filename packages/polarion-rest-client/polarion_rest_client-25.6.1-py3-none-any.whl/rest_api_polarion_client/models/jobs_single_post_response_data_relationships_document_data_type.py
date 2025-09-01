from enum import Enum


class JobsSinglePostResponseDataRelationshipsDocumentDataType(str, Enum):
    DOCUMENTS = "documents"

    def __str__(self) -> str:
        return str(self.value)
