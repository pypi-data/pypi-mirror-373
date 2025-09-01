from enum import Enum


class WorkitemApprovalsSingleGetResponseDataAttributesStatus(str, Enum):
    APPROVED = "approved"
    DISAPPROVED = "disapproved"
    WAITING = "waiting"

    def __str__(self) -> str:
        return str(self.value)
