from enum import Enum


class WorkitemsSingleGetResponseDataRelationshipsApprovalsDataItemType(str, Enum):
    WORKITEM_APPROVALS = "workitem_approvals"

    def __str__(self) -> str:
        return str(self.value)
