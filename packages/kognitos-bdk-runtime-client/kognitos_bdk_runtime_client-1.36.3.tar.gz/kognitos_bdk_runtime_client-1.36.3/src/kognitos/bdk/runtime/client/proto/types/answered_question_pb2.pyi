from types import noun_phrase_pb2 as _noun_phrase_pb2
from types import value_pb2 as _value_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class AnsweredQuestion(_message.Message):
    __slots__ = ('noun_phrases', 'answer')
    NOUN_PHRASES_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    noun_phrases: _noun_phrase_pb2.NounPhrases
    answer: _value_pb2.Value

    def __init__(self, noun_phrases: _Optional[_Union[_noun_phrase_pb2.NounPhrases, _Mapping]]=..., answer: _Optional[_Union[_value_pb2.Value, _Mapping]]=...) -> None:
        ...