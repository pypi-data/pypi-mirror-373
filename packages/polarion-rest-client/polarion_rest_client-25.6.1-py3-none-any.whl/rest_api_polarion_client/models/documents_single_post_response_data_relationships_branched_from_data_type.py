from enum import Enum


class DocumentsSinglePostResponseDataRelationshipsBranchedFromDataType(str, Enum):
    DOCUMENTS = "documents"

    def __str__(self) -> str:
        return str(self.value)
