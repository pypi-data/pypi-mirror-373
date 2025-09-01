from enum import Enum


class FeatureselectionsSingleGetResponseDataType(str, Enum):
    FEATURESELECTIONS = "featureselections"

    def __str__(self) -> str:
        return str(self.value)
