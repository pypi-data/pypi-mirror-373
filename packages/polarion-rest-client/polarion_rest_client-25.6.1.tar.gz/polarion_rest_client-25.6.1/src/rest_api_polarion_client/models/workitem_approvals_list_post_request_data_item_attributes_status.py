from enum import Enum


class WorkitemApprovalsListPostRequestDataItemAttributesStatus(str, Enum):
    APPROVED = "approved"
    DISAPPROVED = "disapproved"
    WAITING = "waiting"

    def __str__(self) -> str:
        return str(self.value)
