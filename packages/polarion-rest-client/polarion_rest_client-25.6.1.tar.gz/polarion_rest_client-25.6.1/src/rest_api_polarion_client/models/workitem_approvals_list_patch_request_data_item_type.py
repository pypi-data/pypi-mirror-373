from enum import Enum


class WorkitemApprovalsListPatchRequestDataItemType(str, Enum):
    WORKITEM_APPROVALS = "workitem_approvals"

    def __str__(self) -> str:
        return str(self.value)
