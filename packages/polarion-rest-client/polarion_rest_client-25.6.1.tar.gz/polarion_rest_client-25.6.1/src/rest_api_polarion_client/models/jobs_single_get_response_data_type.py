from enum import Enum


class JobsSingleGetResponseDataType(str, Enum):
    JOBS = "jobs"

    def __str__(self) -> str:
        return str(self.value)
