from dataclasses import dataclass, field
from typing import List

from .base import BdkDescriptorBase
from .book_authentication_descriptor import BookAuthenticationDescriptor
from .concept_descriptor import ConceptDescriptor
from .noun_phrase import NounPhrase


@dataclass
class BookDescriptor(BdkDescriptorBase):
    id: str
    name: str
    short_description: str
    long_description: str
    author: str
    icon: bytes
    version: str
    authentications: List[BookAuthenticationDescriptor]
    configurations: List[ConceptDescriptor]
    display_name: str
    endpoint: str
    connection_required: bool
    discover_capable: bool
    noun_phrase: NounPhrase
    tags: List[str] = field(default_factory=list)
