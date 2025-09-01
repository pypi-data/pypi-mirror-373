from enum import Enum


class ProjecttemplatesListGetResponseDataItemType(str, Enum):
    PROJECTTEMPLATES = "projecttemplates"

    def __str__(self) -> str:
        return str(self.value)
