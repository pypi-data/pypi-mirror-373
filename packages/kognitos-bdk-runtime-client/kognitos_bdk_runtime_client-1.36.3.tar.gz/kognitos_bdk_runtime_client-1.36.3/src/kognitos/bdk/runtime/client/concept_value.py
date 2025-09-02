from dataclasses import dataclass

from kognitos.bdk.runtime.client.noun_phrase import NounPhrases
from kognitos.bdk.runtime.client.value import Value

from .base import BdkDescriptorBase


@dataclass
class ConceptValue(BdkDescriptorBase):
    noun_phrases: NounPhrases
    value: Value
