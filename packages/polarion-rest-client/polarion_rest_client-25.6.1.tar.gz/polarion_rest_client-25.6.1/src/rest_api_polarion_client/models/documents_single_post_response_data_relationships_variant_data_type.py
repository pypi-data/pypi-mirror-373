from enum import Enum


class DocumentsSinglePostResponseDataRelationshipsVariantDataType(str, Enum):
    WORKITEMS = "workitems"

    def __str__(self) -> str:
        return str(self.value)
