from enum import Enum


class PagesSingleGetResponseDataRelationshipsAttachmentsDataItemType(str, Enum):
    PAGE_ATTACHMENTS = "page_attachments"

    def __str__(self) -> str:
        return str(self.value)
