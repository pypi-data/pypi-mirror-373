from enum import Enum


class TestrunsListPatchRequestDataItemRelationshipsSummaryDefectDataType(str, Enum):
    WORKITEMS = "workitems"

    def __str__(self) -> str:
        return str(self.value)
