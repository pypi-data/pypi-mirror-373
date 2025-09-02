from types import question_pb2 as _question_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class QuestionResponse(_message.Message):
    __slots__ = ('questions',)
    QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    questions: _containers.RepeatedCompositeFieldContainer[_question_pb2.Question]

    def __init__(self, questions: _Optional[_Iterable[_Union[_question_pb2.Question, _Mapping]]]=...) -> None:
        ...