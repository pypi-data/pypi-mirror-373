from enum import Enum


class DocumentPartsListPostRequestDataItemRelationshipsNextPartDataType(str, Enum):
    DOCUMENT_PARTS = "document_parts"

    def __str__(self) -> str:
        return str(self.value)
