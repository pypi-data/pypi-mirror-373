from enum import Enum


class JobsSingleGetResponseDataAttributesStatusType(str, Enum):
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    OK = "OK"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
