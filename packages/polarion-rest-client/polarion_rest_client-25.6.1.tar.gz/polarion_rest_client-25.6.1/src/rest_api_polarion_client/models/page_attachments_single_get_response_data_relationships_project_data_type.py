from enum import Enum


class PageAttachmentsSingleGetResponseDataRelationshipsProjectDataType(str, Enum):
    PROJECTS = "projects"

    def __str__(self) -> str:
        return str(self.value)
