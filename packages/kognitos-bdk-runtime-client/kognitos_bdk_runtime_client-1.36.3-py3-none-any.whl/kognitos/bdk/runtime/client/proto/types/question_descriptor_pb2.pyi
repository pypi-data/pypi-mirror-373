from types import concept_type_pb2 as _concept_type_pb2
from types import noun_phrase_pb2 as _noun_phrase_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class QuestionDescriptor(_message.Message):
    __slots__ = ('noun_phrases', 'type')
    NOUN_PHRASES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    noun_phrases: _noun_phrase_pb2.NounPhrases
    type: _concept_type_pb2.ConceptType

    def __init__(self, noun_phrases: _Optional[_Union[_noun_phrase_pb2.NounPhrases, _Mapping]]=..., type: _Optional[_Union[_concept_type_pb2.ConceptType, _Mapping]]=...) -> None:
        ...