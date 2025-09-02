from dataclasses import dataclass
from enum import Enum
from typing import List, Union

from .base import BdkDescriptorBase
from .noun_phrase import NounPhrase


@dataclass
class ConceptTableTypeColumn(BdkDescriptorBase):
    key: str
    value: "ConceptType"


class ConceptScalarType(Enum):
    CONCEPT_SCALAR_TYPE_CONCEPTUAL = 0
    CONCEPT_SCALAR_TYPE_TEXT = 1
    CONCEPT_SCALAR_TYPE_NUMBER = 2
    CONCEPT_SCALAR_TYPE_BOOLEAN = 3
    CONCEPT_SCALAR_TYPE_DATETIME = 4
    CONCEPT_SCALAR_TYPE_DATE = 5
    CONCEPT_SCALAR_TYPE_TIME = 6
    CONCEPT_SCALAR_TYPE_FILE = 7
    CONCEPT_SCALAR_TYPE_UUID = 8

    def human_readable(self) -> str:
        return self.name.replace("CONCEPT_SCALAR_TYPE_", "")


@dataclass
class ConceptOptionalType(BdkDescriptorBase):
    inner: "ConceptType"


@dataclass
class ConceptSensitiveType(BdkDescriptorBase):
    inner: "ConceptType"


@dataclass
class ConceptListType(BdkDescriptorBase):
    inner: "ConceptType"


@dataclass
class ConceptDictionaryTypeField(BdkDescriptorBase):
    key: str
    value: "ConceptType"
    description: str


@dataclass
class ConceptDictionaryType(BdkDescriptorBase):
    is_a: List[NounPhrase]
    fields: List[ConceptDictionaryTypeField]
    description: str

    def human_readable(self) -> str:
        """
        Returns a string representation of the DictionaryValue.
        """
        str_is_a = [str(is_a) for is_a in self.is_a]
        return f"Object({', '.join(str_is_a)})"


@dataclass
class ConceptTableType(BdkDescriptorBase):
    columns: List[ConceptTableTypeColumn]
    description: str

    def human_readable(self) -> str:
        """
        Returns a string representation of a Table.
        """
        str_columns = [column.key for column in self.columns]
        return f"Table with columns: {', '.join(str_columns)}"


@dataclass
class ConceptOpaqueType(BdkDescriptorBase):
    is_a: List[NounPhrase]
    description: str

    def human_readable(self) -> str:
        """
        Returns a string representation of the OpaqueValue.
        """
        str_is_a = [str(is_a) for is_a in self.is_a]
        return f"Object({', '.join(str_is_a)})"


@dataclass
class ConceptAnyType(BdkDescriptorBase):
    pass


@dataclass
class ConceptSelfType(BdkDescriptorBase):
    pass


@dataclass
class ConceptUnionType(BdkDescriptorBase):
    inners: List["ConceptType"]


@dataclass
class ConceptEnumTypeMember(BdkDescriptorBase):
    name: str
    noun_phrase: NounPhrase
    description: str


@dataclass
class ConceptEnumType(BdkDescriptorBase):
    is_a: List[NounPhrase]
    members: List[ConceptEnumTypeMember]
    description: str

    def human_readable(self) -> str:
        """
        Returns a string representation of the EnumValue.
        """
        str_is_a = [str(is_a) for is_a in self.is_a]
        return f"Enum({', '.join(str_is_a)})"


ConceptType = Union[
    ConceptScalarType,
    ConceptOptionalType,
    ConceptListType,
    ConceptDictionaryType,
    ConceptTableType,
    ConceptOpaqueType,
    ConceptAnyType,
    ConceptUnionType,
    ConceptSelfType,
    ConceptSensitiveType,
    ConceptEnumType,
]
