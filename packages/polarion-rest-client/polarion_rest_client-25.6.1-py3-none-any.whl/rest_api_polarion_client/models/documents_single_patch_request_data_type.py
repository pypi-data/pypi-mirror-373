from enum import Enum


class DocumentsSinglePatchRequestDataType(str, Enum):
    DOCUMENTS = "documents"

    def __str__(self) -> str:
        return str(self.value)
