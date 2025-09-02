from types import book_procedure_signature_pb2 as _book_procedure_signature_pb2
from types import concept_descriptor_pb2 as _concept_descriptor_pb2
from types import connection_required_pb2 as _connection_required_pb2
from types import example_descriptor_pb2 as _example_descriptor_pb2
from types import question_descriptor_pb2 as _question_descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class BookProcedureDescriptor(_message.Message):
    __slots__ = ('id', 'signature', 'inputs', 'outputs', 'short_description', 'long_description', 'filter_capable', 'page_capable', 'connection_required', 'is_discovered', 'questions', 'examples', 'is_async', 'connection_requirement_level')
    ID_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    SHORT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LONG_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILTER_CAPABLE_FIELD_NUMBER: _ClassVar[int]
    PAGE_CAPABLE_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    IS_DISCOVERED_FIELD_NUMBER: _ClassVar[int]
    QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    EXAMPLES_FIELD_NUMBER: _ClassVar[int]
    IS_ASYNC_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_REQUIREMENT_LEVEL_FIELD_NUMBER: _ClassVar[int]
    id: str
    signature: _book_procedure_signature_pb2.BookProcedureSignature
    inputs: _containers.RepeatedCompositeFieldContainer[_concept_descriptor_pb2.ConceptDescriptor]
    outputs: _containers.RepeatedCompositeFieldContainer[_concept_descriptor_pb2.ConceptDescriptor]
    short_description: str
    long_description: str
    filter_capable: bool
    page_capable: bool
    connection_required: bool
    is_discovered: bool
    questions: _containers.RepeatedCompositeFieldContainer[_question_descriptor_pb2.QuestionDescriptor]
    examples: _containers.RepeatedCompositeFieldContainer[_example_descriptor_pb2.ExampleDescriptor]
    is_async: bool
    connection_requirement_level: _connection_required_pb2.ConnectionRequired

    def __init__(self, id: _Optional[str]=..., signature: _Optional[_Union[_book_procedure_signature_pb2.BookProcedureSignature, _Mapping]]=..., inputs: _Optional[_Iterable[_Union[_concept_descriptor_pb2.ConceptDescriptor, _Mapping]]]=..., outputs: _Optional[_Iterable[_Union[_concept_descriptor_pb2.ConceptDescriptor, _Mapping]]]=..., short_description: _Optional[str]=..., long_description: _Optional[str]=..., filter_capable: bool=..., page_capable: bool=..., connection_required: bool=..., is_discovered: bool=..., questions: _Optional[_Iterable[_Union[_question_descriptor_pb2.QuestionDescriptor, _Mapping]]]=..., examples: _Optional[_Iterable[_Union[_example_descriptor_pb2.ExampleDescriptor, _Mapping]]]=..., is_async: bool=..., connection_requirement_level: _Optional[_Union[_connection_required_pb2.ConnectionRequired, str]]=...) -> None:
        ...

class BookProcedureDescriptorV2(_message.Message):
    __slots__ = ('id', 'signature', 'inputs', 'outputs', 'short_description', 'long_description', 'filter_capable', 'page_capable', 'connection_required', 'is_discovered', 'questions', 'examples', 'is_async')
    ID_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    SHORT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LONG_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILTER_CAPABLE_FIELD_NUMBER: _ClassVar[int]
    PAGE_CAPABLE_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    IS_DISCOVERED_FIELD_NUMBER: _ClassVar[int]
    QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    EXAMPLES_FIELD_NUMBER: _ClassVar[int]
    IS_ASYNC_FIELD_NUMBER: _ClassVar[int]
    id: str
    signature: _book_procedure_signature_pb2.BookProcedureSignature
    inputs: _containers.RepeatedCompositeFieldContainer[_concept_descriptor_pb2.ConceptDescriptor]
    outputs: _containers.RepeatedCompositeFieldContainer[_concept_descriptor_pb2.ConceptDescriptor]
    short_description: str
    long_description: str
    filter_capable: bool
    page_capable: bool
    connection_required: _connection_required_pb2.ConnectionRequired
    is_discovered: bool
    questions: _containers.RepeatedCompositeFieldContainer[_question_descriptor_pb2.QuestionDescriptor]
    examples: _containers.RepeatedCompositeFieldContainer[_example_descriptor_pb2.ExampleDescriptor]
    is_async: bool

    def __init__(self, id: _Optional[str]=..., signature: _Optional[_Union[_book_procedure_signature_pb2.BookProcedureSignature, _Mapping]]=..., inputs: _Optional[_Iterable[_Union[_concept_descriptor_pb2.ConceptDescriptor, _Mapping]]]=..., outputs: _Optional[_Iterable[_Union[_concept_descriptor_pb2.ConceptDescriptor, _Mapping]]]=..., short_description: _Optional[str]=..., long_description: _Optional[str]=..., filter_capable: bool=..., page_capable: bool=..., connection_required: _Optional[_Union[_connection_required_pb2.ConnectionRequired, str]]=..., is_discovered: bool=..., questions: _Optional[_Iterable[_Union[_question_descriptor_pb2.QuestionDescriptor, _Mapping]]]=..., examples: _Optional[_Iterable[_Union[_example_descriptor_pb2.ExampleDescriptor, _Mapping]]]=..., is_async: bool=...) -> None:
        ...