from dataclasses import dataclass
from typing import List

from .base import BdkDescriptorBase
from .noun_phrase import NounPhrases


@dataclass
class BookProcedureSignature(BdkDescriptorBase):
    english: str
    preposition: str
    is_read_only: bool
    verbs: List[str]
    object: NounPhrases
    outputs: List[NounPhrases]
    target: NounPhrases
    proper_nouns: List[str]
