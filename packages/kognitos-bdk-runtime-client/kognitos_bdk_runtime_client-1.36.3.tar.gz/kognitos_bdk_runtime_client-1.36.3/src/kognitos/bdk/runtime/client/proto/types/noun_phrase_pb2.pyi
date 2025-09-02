from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class NounPhrase(_message.Message):
    __slots__ = ('modifiers', 'head')
    MODIFIERS_FIELD_NUMBER: _ClassVar[int]
    HEAD_FIELD_NUMBER: _ClassVar[int]
    modifiers: _containers.RepeatedScalarFieldContainer[str]
    head: str

    def __init__(self, modifiers: _Optional[_Iterable[str]]=..., head: _Optional[str]=...) -> None:
        ...

class NounPhrases(_message.Message):
    __slots__ = ('noun_phrases',)
    NOUN_PHRASES_FIELD_NUMBER: _ClassVar[int]
    noun_phrases: _containers.RepeatedCompositeFieldContainer[NounPhrase]

    def __init__(self, noun_phrases: _Optional[_Iterable[_Union[NounPhrase, _Mapping]]]=...) -> None:
        ...