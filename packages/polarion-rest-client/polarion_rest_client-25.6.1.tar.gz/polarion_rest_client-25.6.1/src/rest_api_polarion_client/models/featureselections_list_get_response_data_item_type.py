from enum import Enum


class FeatureselectionsListGetResponseDataItemType(str, Enum):
    FEATURESELECTIONS = "featureselections"

    def __str__(self) -> str:
        return str(self.value)
