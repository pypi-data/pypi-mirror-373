from dataclasses import dataclass

from .base import BdkDescriptorBase
from .noun_phrase import NounPhrases
from .value import Value


@dataclass
class InputConcept(BdkDescriptorBase):
    noun_phrases: NounPhrases
    value: Value
