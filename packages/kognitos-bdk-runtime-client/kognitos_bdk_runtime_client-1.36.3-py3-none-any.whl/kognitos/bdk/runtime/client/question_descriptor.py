from dataclasses import dataclass

from .base import BdkDescriptorBase
from .concept_type import ConceptType
from .noun_phrase import NounPhrases


@dataclass
class QuestionDescriptor(BdkDescriptorBase):
    noun_phrases: NounPhrases
    type: ConceptType
