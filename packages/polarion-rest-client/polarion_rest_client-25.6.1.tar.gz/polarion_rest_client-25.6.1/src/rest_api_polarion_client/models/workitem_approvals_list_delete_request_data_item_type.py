from enum import Enum


class WorkitemApprovalsListDeleteRequestDataItemType(str, Enum):
    WORKITEM_APPROVALS = "workitem_approvals"

    def __str__(self) -> str:
        return str(self.value)
