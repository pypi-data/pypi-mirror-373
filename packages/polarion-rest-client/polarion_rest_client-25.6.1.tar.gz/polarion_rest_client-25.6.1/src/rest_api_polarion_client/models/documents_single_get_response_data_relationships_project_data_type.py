from enum import Enum


class DocumentsSingleGetResponseDataRelationshipsProjectDataType(str, Enum):
    PROJECTS = "projects"

    def __str__(self) -> str:
        return str(self.value)
