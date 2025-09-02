from requests import authentication_pb2 as _authentication_pb2
from requests import offload_pb2 as _offload_pb2
from types import answered_question_pb2 as _answered_question_pb2
from types import concept_value_pb2 as _concept_value_pb2
from types import promise_pb2 as _promise_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class ResolvePromiseRequest(_message.Message):
    __slots__ = ('name', 'version', 'authentication', 'procedure_id', 'promise', 'offload', 'answered_questions', 'configurations')
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_FIELD_NUMBER: _ClassVar[int]
    PROCEDURE_ID_FIELD_NUMBER: _ClassVar[int]
    PROMISE_FIELD_NUMBER: _ClassVar[int]
    OFFLOAD_FIELD_NUMBER: _ClassVar[int]
    ANSWERED_QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    authentication: _authentication_pb2.Authentication
    procedure_id: str
    promise: _promise_pb2.Promise
    offload: _offload_pb2.Offload
    answered_questions: _containers.RepeatedCompositeFieldContainer[_answered_question_pb2.AnsweredQuestion]
    configurations: _containers.RepeatedCompositeFieldContainer[_concept_value_pb2.ConceptValue]

    def __init__(self, name: _Optional[str]=..., version: _Optional[str]=..., authentication: _Optional[_Union[_authentication_pb2.Authentication, _Mapping]]=..., procedure_id: _Optional[str]=..., promise: _Optional[_Union[_promise_pb2.Promise, _Mapping]]=..., offload: _Optional[_Union[_offload_pb2.Offload, _Mapping]]=..., answered_questions: _Optional[_Iterable[_Union[_answered_question_pb2.AnsweredQuestion, _Mapping]]]=..., configurations: _Optional[_Iterable[_Union[_concept_value_pb2.ConceptValue, _Mapping]]]=...) -> None:
        ...