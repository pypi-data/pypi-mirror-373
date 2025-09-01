from enum import Enum


class WorkitemsListGetResponseDataItemRelationshipsAttachmentsDataItemType(str, Enum):
    WORKITEM_ATTACHMENTS = "workitem_attachments"

    def __str__(self) -> str:
        return str(self.value)
