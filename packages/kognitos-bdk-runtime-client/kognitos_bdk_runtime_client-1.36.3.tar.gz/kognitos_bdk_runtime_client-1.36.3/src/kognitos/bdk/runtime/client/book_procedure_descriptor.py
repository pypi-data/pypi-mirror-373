from dataclasses import dataclass, field
from typing import List

from .base import BdkDescriptorBase
from .book_procedure_signature import BookProcedureSignature
from .concept_descriptor import ConceptDescriptor
from .connection_required import ConnectionRequired
from .example_descriptor import ExampleDescriptor
from .question_descriptor import QuestionDescriptor


@dataclass
class BookProcedureDescriptor(BdkDescriptorBase):
    id: str
    short_description: str
    long_description: str
    signature: BookProcedureSignature
    inputs: List[ConceptDescriptor]
    outputs: List[ConceptDescriptor]
    filter_capable: bool
    page_capable: bool
    connection_required: ConnectionRequired
    examples: List[ExampleDescriptor] = field(default_factory=list)
    questions: List[QuestionDescriptor] = field(default_factory=list)
