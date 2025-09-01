from enum import Enum


class TestrunsListGetResponseDataItemRelationshipsDocumentDataType(str, Enum):
    DOCUMENTS = "documents"

    def __str__(self) -> str:
        return str(self.value)
