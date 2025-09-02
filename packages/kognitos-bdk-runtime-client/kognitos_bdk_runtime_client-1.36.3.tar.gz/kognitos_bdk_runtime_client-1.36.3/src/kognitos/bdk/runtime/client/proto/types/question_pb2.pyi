from types import concept_type_pb2 as _concept_type_pb2
from types import noun_phrase_pb2 as _noun_phrase_pb2
from types import value_pb2 as _value_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Question(_message.Message):
    __slots__ = ('noun_phrases', 'concept_type', 'choices', 'text')
    NOUN_PHRASES_FIELD_NUMBER: _ClassVar[int]
    CONCEPT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    noun_phrases: _noun_phrase_pb2.NounPhrases
    concept_type: _concept_type_pb2.ConceptType
    choices: _containers.RepeatedCompositeFieldContainer[_value_pb2.Value]
    text: str

    def __init__(self, noun_phrases: _Optional[_Union[_noun_phrase_pb2.NounPhrases, _Mapping]]=..., concept_type: _Optional[_Union[_concept_type_pb2.ConceptType, _Mapping]]=..., choices: _Optional[_Iterable[_Union[_value_pb2.Value, _Mapping]]]=..., text: _Optional[str]=...) -> None:
        ...