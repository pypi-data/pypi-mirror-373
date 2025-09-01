from enum import Enum


class FeatureselectionsListGetResponseDataItemAttributesSelectionType(str, Enum):
    EXCLUDED = "excluded"
    IMPLICITLY_INCLUDED = "implicitly-included"
    INCLUDED = "included"

    def __str__(self) -> str:
        return str(self.value)
