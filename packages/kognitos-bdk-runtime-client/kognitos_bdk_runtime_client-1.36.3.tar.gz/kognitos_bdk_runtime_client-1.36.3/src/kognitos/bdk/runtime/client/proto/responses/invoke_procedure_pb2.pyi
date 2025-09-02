from responses import promise_pb2 as _promise_pb2
from responses import question_pb2 as _question_pb2
from types import concept_value_pb2 as _concept_value_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class InvokeProcedureResponse(_message.Message):
    __slots__ = ('output_concepts',)
    OUTPUT_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    output_concepts: _containers.RepeatedCompositeFieldContainer[_concept_value_pb2.ConceptValue]

    def __init__(self, output_concepts: _Optional[_Iterable[_Union[_concept_value_pb2.ConceptValue, _Mapping]]]=...) -> None:
        ...

class InvokeProcedureResponseV2(_message.Message):
    __slots__ = ('response', 'question', 'promise')
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    PROMISE_FIELD_NUMBER: _ClassVar[int]
    response: InvokeProcedureResponse
    question: _question_pb2.QuestionResponse
    promise: _promise_pb2.PromiseResponse

    def __init__(self, response: _Optional[_Union[InvokeProcedureResponse, _Mapping]]=..., question: _Optional[_Union[_question_pb2.QuestionResponse, _Mapping]]=..., promise: _Optional[_Union[_promise_pb2.PromiseResponse, _Mapping]]=...) -> None:
        ...