from types import noun_phrase_pb2 as _noun_phrase_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class ConceptScalarType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ConceptScalarTypeConceptual: _ClassVar[ConceptScalarType]
    ConceptScalarTypeText: _ClassVar[ConceptScalarType]
    ConceptScalarTypeNumber: _ClassVar[ConceptScalarType]
    ConceptScalarTypeBoolean: _ClassVar[ConceptScalarType]
    ConceptScalarTypeDatetime: _ClassVar[ConceptScalarType]
    ConceptScalarTypeDate: _ClassVar[ConceptScalarType]
    ConceptScalarTypeTime: _ClassVar[ConceptScalarType]
    ConceptScalarTypeFile: _ClassVar[ConceptScalarType]
    ConceptScalarTypeUUID: _ClassVar[ConceptScalarType]
ConceptScalarTypeConceptual: ConceptScalarType
ConceptScalarTypeText: ConceptScalarType
ConceptScalarTypeNumber: ConceptScalarType
ConceptScalarTypeBoolean: ConceptScalarType
ConceptScalarTypeDatetime: ConceptScalarType
ConceptScalarTypeDate: ConceptScalarType
ConceptScalarTypeTime: ConceptScalarType
ConceptScalarTypeFile: ConceptScalarType
ConceptScalarTypeUUID: ConceptScalarType

class ConceptOptionalType(_message.Message):
    __slots__ = ('inner',)
    INNER_FIELD_NUMBER: _ClassVar[int]
    inner: ConceptType

    def __init__(self, inner: _Optional[_Union[ConceptType, _Mapping]]=...) -> None:
        ...

class ConceptSensitiveType(_message.Message):
    __slots__ = ('inner',)
    INNER_FIELD_NUMBER: _ClassVar[int]
    inner: ConceptType

    def __init__(self, inner: _Optional[_Union[ConceptType, _Mapping]]=...) -> None:
        ...

class ConceptListType(_message.Message):
    __slots__ = ('inner',)
    INNER_FIELD_NUMBER: _ClassVar[int]
    inner: ConceptType

    def __init__(self, inner: _Optional[_Union[ConceptType, _Mapping]]=...) -> None:
        ...

class ConceptUnionType(_message.Message):
    __slots__ = ('inners',)
    INNERS_FIELD_NUMBER: _ClassVar[int]
    inners: _containers.RepeatedCompositeFieldContainer[ConceptType]

    def __init__(self, inners: _Optional[_Iterable[_Union[ConceptType, _Mapping]]]=...) -> None:
        ...

class ConceptDictionaryType(_message.Message):
    __slots__ = ('is_a', 'fields', 'description')
    IS_A_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    is_a: _containers.RepeatedCompositeFieldContainer[_noun_phrase_pb2.NounPhrase]
    fields: _containers.RepeatedCompositeFieldContainer[ConceptDictionaryTypeField]
    description: str

    def __init__(self, is_a: _Optional[_Iterable[_Union[_noun_phrase_pb2.NounPhrase, _Mapping]]]=..., fields: _Optional[_Iterable[_Union[ConceptDictionaryTypeField, _Mapping]]]=..., description: _Optional[str]=...) -> None:
        ...

class ConceptDictionaryTypeField(_message.Message):
    __slots__ = ('key', 'value', 'description')
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: ConceptType
    description: str

    def __init__(self, key: _Optional[str]=..., value: _Optional[_Union[ConceptType, _Mapping]]=..., description: _Optional[str]=...) -> None:
        ...

class ConceptTableType(_message.Message):
    __slots__ = ('columns', 'description')
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    columns: _containers.RepeatedCompositeFieldContainer[ConceptTableTypeColumn]
    description: str

    def __init__(self, columns: _Optional[_Iterable[_Union[ConceptTableTypeColumn, _Mapping]]]=..., description: _Optional[str]=...) -> None:
        ...

class ConceptTableTypeColumn(_message.Message):
    __slots__ = ('key', 'value', 'description')
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: ConceptType
    description: str

    def __init__(self, key: _Optional[str]=..., value: _Optional[_Union[ConceptType, _Mapping]]=..., description: _Optional[str]=...) -> None:
        ...

class ConceptOpaqueType(_message.Message):
    __slots__ = ('is_a', 'description')
    IS_A_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    is_a: _containers.RepeatedCompositeFieldContainer[_noun_phrase_pb2.NounPhrase]
    description: str

    def __init__(self, is_a: _Optional[_Iterable[_Union[_noun_phrase_pb2.NounPhrase, _Mapping]]]=..., description: _Optional[str]=...) -> None:
        ...

class ConceptAnyType(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ConceptSelfType(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ConceptEnumTypeMember(_message.Message):
    __slots__ = ('name', 'noun_phrase', 'description')
    NAME_FIELD_NUMBER: _ClassVar[int]
    NOUN_PHRASE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    noun_phrase: _noun_phrase_pb2.NounPhrase
    description: str

    def __init__(self, name: _Optional[str]=..., noun_phrase: _Optional[_Union[_noun_phrase_pb2.NounPhrase, _Mapping]]=..., description: _Optional[str]=...) -> None:
        ...

class ConceptEnumType(_message.Message):
    __slots__ = ('is_a', 'members', 'description')
    IS_A_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    is_a: _containers.RepeatedCompositeFieldContainer[_noun_phrase_pb2.NounPhrase]
    members: _containers.RepeatedCompositeFieldContainer[ConceptEnumTypeMember]
    description: str

    def __init__(self, is_a: _Optional[_Iterable[_Union[_noun_phrase_pb2.NounPhrase, _Mapping]]]=..., members: _Optional[_Iterable[_Union[ConceptEnumTypeMember, _Mapping]]]=..., description: _Optional[str]=...) -> None:
        ...

class ConceptType(_message.Message):
    __slots__ = ('scalar_type', 'optional_type', 'list_type', 'dictionary_type', 'table_type', 'opaque_type', 'any_type', 'union_type', 'self_type', 'sensitive_type', 'enum_type')
    SCALAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    LIST_TYPE_FIELD_NUMBER: _ClassVar[int]
    DICTIONARY_TYPE_FIELD_NUMBER: _ClassVar[int]
    TABLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPAQUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ANY_TYPE_FIELD_NUMBER: _ClassVar[int]
    UNION_TYPE_FIELD_NUMBER: _ClassVar[int]
    SELF_TYPE_FIELD_NUMBER: _ClassVar[int]
    SENSITIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENUM_TYPE_FIELD_NUMBER: _ClassVar[int]
    scalar_type: ConceptScalarType
    optional_type: ConceptOptionalType
    list_type: ConceptListType
    dictionary_type: ConceptDictionaryType
    table_type: ConceptTableType
    opaque_type: ConceptOpaqueType
    any_type: ConceptAnyType
    union_type: ConceptUnionType
    self_type: ConceptSelfType
    sensitive_type: ConceptSensitiveType
    enum_type: ConceptEnumType

    def __init__(self, scalar_type: _Optional[_Union[ConceptScalarType, str]]=..., optional_type: _Optional[_Union[ConceptOptionalType, _Mapping]]=..., list_type: _Optional[_Union[ConceptListType, _Mapping]]=..., dictionary_type: _Optional[_Union[ConceptDictionaryType, _Mapping]]=..., table_type: _Optional[_Union[ConceptTableType, _Mapping]]=..., opaque_type: _Optional[_Union[ConceptOpaqueType, _Mapping]]=..., any_type: _Optional[_Union[ConceptAnyType, _Mapping]]=..., union_type: _Optional[_Union[ConceptUnionType, _Mapping]]=..., self_type: _Optional[_Union[ConceptSelfType, _Mapping]]=..., sensitive_type: _Optional[_Union[ConceptSensitiveType, _Mapping]]=..., enum_type: _Optional[_Union[ConceptEnumType, _Mapping]]=...) -> None:
        ...