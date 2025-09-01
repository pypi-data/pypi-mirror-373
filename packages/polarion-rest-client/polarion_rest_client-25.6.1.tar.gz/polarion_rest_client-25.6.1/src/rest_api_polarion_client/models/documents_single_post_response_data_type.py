from enum import Enum


class DocumentsSinglePostResponseDataType(str, Enum):
    DOCUMENTS = "documents"

    def __str__(self) -> str:
        return str(self.value)
