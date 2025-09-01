from enum import Enum


class PlansSingleGetResponseDataRelationshipsProjectSpanDataItemType(str, Enum):
    PROJECTS = "projects"

    def __str__(self) -> str:
        return str(self.value)
