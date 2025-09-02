from types import noun_phrase_pb2 as _noun_phrase_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class BookProcedureSignature(_message.Message):
    __slots__ = ('english', 'verbs', 'object', 'preposition', 'target', 'outputs', 'is_read_only', 'proper_nouns')
    ENGLISH_FIELD_NUMBER: _ClassVar[int]
    VERBS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    PREPOSITION_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    IS_READ_ONLY_FIELD_NUMBER: _ClassVar[int]
    PROPER_NOUNS_FIELD_NUMBER: _ClassVar[int]
    english: str
    verbs: _containers.RepeatedScalarFieldContainer[str]
    object: _noun_phrase_pb2.NounPhrases
    preposition: str
    target: _noun_phrase_pb2.NounPhrases
    outputs: _containers.RepeatedCompositeFieldContainer[_noun_phrase_pb2.NounPhrases]
    is_read_only: bool
    proper_nouns: _containers.RepeatedScalarFieldContainer[str]

    def __init__(self, english: _Optional[str]=..., verbs: _Optional[_Iterable[str]]=..., object: _Optional[_Union[_noun_phrase_pb2.NounPhrases, _Mapping]]=..., preposition: _Optional[str]=..., target: _Optional[_Union[_noun_phrase_pb2.NounPhrases, _Mapping]]=..., outputs: _Optional[_Iterable[_Union[_noun_phrase_pb2.NounPhrases, _Mapping]]]=..., is_read_only: bool=..., proper_nouns: _Optional[_Iterable[str]]=...) -> None:
        ...