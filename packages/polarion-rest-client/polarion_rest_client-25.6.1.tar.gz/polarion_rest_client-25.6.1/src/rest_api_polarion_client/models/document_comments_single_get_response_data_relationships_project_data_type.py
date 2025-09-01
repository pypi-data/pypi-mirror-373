from enum import Enum


class DocumentCommentsSingleGetResponseDataRelationshipsProjectDataType(str, Enum):
    PROJECTS = "projects"

    def __str__(self) -> str:
        return str(self.value)
