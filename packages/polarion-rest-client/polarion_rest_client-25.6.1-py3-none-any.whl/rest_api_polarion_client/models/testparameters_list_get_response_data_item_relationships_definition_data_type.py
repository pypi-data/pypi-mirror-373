from enum import Enum


class TestparametersListGetResponseDataItemRelationshipsDefinitionDataType(str, Enum):
    TESTPARAMETER_DEFINITIONS = "testparameter_definitions"

    def __str__(self) -> str:
        return str(self.value)
