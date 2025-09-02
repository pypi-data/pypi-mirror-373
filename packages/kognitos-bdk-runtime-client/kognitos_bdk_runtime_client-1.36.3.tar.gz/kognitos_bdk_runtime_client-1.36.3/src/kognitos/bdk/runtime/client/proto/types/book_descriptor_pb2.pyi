from types import book_authentication_descriptor_pb2 as _book_authentication_descriptor_pb2
from types import book_procedure_descriptor_pb2 as _book_procedure_descriptor_pb2
from types import concept_descriptor_pb2 as _concept_descriptor_pb2
from types import noun_phrase_pb2 as _noun_phrase_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class BookDescriptor(_message.Message):
    __slots__ = ('id', 'name', 'short_description', 'long_description', 'author', 'icon', 'version', 'authentications', 'configurations', 'display_name', 'endpoint', 'connection_required', 'discover_capable', 'tags', 'procedures', 'noun_phrase')
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LONG_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATIONS_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    DISCOVER_CAPABLE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    PROCEDURES_FIELD_NUMBER: _ClassVar[int]
    NOUN_PHRASE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    short_description: str
    long_description: str
    author: str
    icon: bytes
    version: str
    authentications: _containers.RepeatedCompositeFieldContainer[_book_authentication_descriptor_pb2.BookAuthenticationDescriptor]
    configurations: _containers.RepeatedCompositeFieldContainer[_concept_descriptor_pb2.ConceptDescriptor]
    display_name: str
    endpoint: str
    connection_required: bool
    discover_capable: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    procedures: _containers.RepeatedCompositeFieldContainer[_book_procedure_descriptor_pb2.BookProcedureDescriptorV2]
    noun_phrase: _noun_phrase_pb2.NounPhrase

    def __init__(self, id: _Optional[str]=..., name: _Optional[str]=..., short_description: _Optional[str]=..., long_description: _Optional[str]=..., author: _Optional[str]=..., icon: _Optional[bytes]=..., version: _Optional[str]=..., authentications: _Optional[_Iterable[_Union[_book_authentication_descriptor_pb2.BookAuthenticationDescriptor, _Mapping]]]=..., configurations: _Optional[_Iterable[_Union[_concept_descriptor_pb2.ConceptDescriptor, _Mapping]]]=..., display_name: _Optional[str]=..., endpoint: _Optional[str]=..., connection_required: bool=..., discover_capable: bool=..., tags: _Optional[_Iterable[str]]=..., procedures: _Optional[_Iterable[_Union[_book_procedure_descriptor_pb2.BookProcedureDescriptorV2, _Mapping]]]=..., noun_phrase: _Optional[_Union[_noun_phrase_pb2.NounPhrase, _Mapping]]=...) -> None:
        ...