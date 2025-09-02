from dataclasses import dataclass

from .base import BdkDescriptorBase
from .concept_type import ConceptType
from .noun_phrase import NounPhrases
from .value import Value


@dataclass
class ConceptDescriptor(BdkDescriptorBase):
    description: str
    type: ConceptType
    noun_phrases: NounPhrases
    default_value: Value
