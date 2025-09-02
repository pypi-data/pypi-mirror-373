from requests import authentication_pb2 as _authentication_pb2
from requests import offload_pb2 as _offload_pb2
from types import answered_question_pb2 as _answered_question_pb2
from types import concept_value_pb2 as _concept_value_pb2
from types import expression_pb2 as _expression_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class InvokeProcedureRequest(_message.Message):
    __slots__ = ('name', 'version', 'authentication', 'procedure_id', 'input_concepts', 'filter_expression', 'offload', 'offset', 'limit', 'answered_questions')
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_FIELD_NUMBER: _ClassVar[int]
    PROCEDURE_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_CONCEPTS_FIELD_NUMBER: _ClassVar[int]
    FILTER_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    OFFLOAD_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    ANSWERED_QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    authentication: _authentication_pb2.Authentication
    procedure_id: str
    input_concepts: _containers.RepeatedCompositeFieldContainer[_concept_value_pb2.ConceptValue]
    filter_expression: _expression_pb2.Expression
    offload: _offload_pb2.Offload
    offset: int
    limit: int
    answered_questions: _containers.RepeatedCompositeFieldContainer[_answered_question_pb2.AnsweredQuestion]

    def __init__(self, name: _Optional[str]=..., version: _Optional[str]=..., authentication: _Optional[_Union[_authentication_pb2.Authentication, _Mapping]]=..., procedure_id: _Optional[str]=..., input_concepts: _Optional[_Iterable[_Union[_concept_value_pb2.ConceptValue, _Mapping]]]=..., filter_expression: _Optional[_Union[_expression_pb2.Expression, _Mapping]]=..., offload: _Optional[_Union[_offload_pb2.Offload, _Mapping]]=..., offset: _Optional[int]=..., limit: _Optional[int]=..., answered_questions: _Optional[_Iterable[_Union[_answered_question_pb2.AnsweredQuestion, _Mapping]]]=...) -> None:
        ...