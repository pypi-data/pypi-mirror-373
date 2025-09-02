from types import concept_type_pb2 as _concept_type_pb2
from types import noun_phrase_pb2 as _noun_phrase_pb2
from types import value_pb2 as _value_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class ConceptDescriptor(_message.Message):
    __slots__ = ('noun_phrases', 'type', 'description', 'default_value')
    NOUN_PHRASES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    noun_phrases: _noun_phrase_pb2.NounPhrases
    type: _concept_type_pb2.ConceptType
    description: str
    default_value: _value_pb2.Value

    def __init__(self, noun_phrases: _Optional[_Union[_noun_phrase_pb2.NounPhrases, _Mapping]]=..., type: _Optional[_Union[_concept_type_pb2.ConceptType, _Mapping]]=..., description: _Optional[str]=..., default_value: _Optional[_Union[_value_pb2.Value, _Mapping]]=...) -> None:
        ...