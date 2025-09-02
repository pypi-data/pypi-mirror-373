from dataclasses import dataclass
from typing import List, Optional

from .base import BdkDescriptorBase
from .concept_type import ConceptType
from .noun_phrase import NounPhrases
from .value import Value


@dataclass
class Question(BdkDescriptorBase):
    noun_phrases: NounPhrases
    concept_type: ConceptType
    choices: Optional[List[Value]] = None
    text: Optional[str] = None


@dataclass
class AnsweredQuestion(BdkDescriptorBase):
    noun_phrases: NounPhrases
    answer: Value
