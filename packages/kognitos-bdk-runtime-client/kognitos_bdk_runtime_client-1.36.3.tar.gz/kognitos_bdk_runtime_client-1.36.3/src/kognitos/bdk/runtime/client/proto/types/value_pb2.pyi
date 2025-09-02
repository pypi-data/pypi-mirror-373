from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from types import concept_type_pb2 as _concept_type_pb2
from types import date_pb2 as _date_pb2
from types import noun_phrase_pb2 as _noun_phrase_pb2
from types import time_pb2 as _time_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Value(_message.Message):
    __slots__ = ('null_value', 'conceptual_value', 'text_value', 'number_value', 'boolean_value', 'datetime_value', 'date_value', 'time_value', 'file_value', 'dictionary_value', 'list_value', 'opaque_value', 'table_value', 'sensitive_value')
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    CONCEPTUAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOLEAN_VALUE_FIELD_NUMBER: _ClassVar[int]
    DATETIME_VALUE_FIELD_NUMBER: _ClassVar[int]
    DATE_VALUE_FIELD_NUMBER: _ClassVar[int]
    TIME_VALUE_FIELD_NUMBER: _ClassVar[int]
    FILE_VALUE_FIELD_NUMBER: _ClassVar[int]
    DICTIONARY_VALUE_FIELD_NUMBER: _ClassVar[int]
    LIST_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPAQUE_VALUE_FIELD_NUMBER: _ClassVar[int]
    TABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    SENSITIVE_VALUE_FIELD_NUMBER: _ClassVar[int]
    null_value: _struct_pb2.NullValue
    conceptual_value: _noun_phrase_pb2.NounPhrase
    text_value: str
    number_value: float
    boolean_value: bool
    datetime_value: _timestamp_pb2.Timestamp
    date_value: _date_pb2.Date
    time_value: _time_pb2.Time
    file_value: FileValue
    dictionary_value: DictionaryValue
    list_value: ListValue
    opaque_value: OpaqueValue
    table_value: TableValue
    sensitive_value: SensitiveValue

    def __init__(self, null_value: _Optional[_Union[_struct_pb2.NullValue, str]]=..., conceptual_value: _Optional[_Union[_noun_phrase_pb2.NounPhrase, _Mapping]]=..., text_value: _Optional[str]=..., number_value: _Optional[float]=..., boolean_value: bool=..., datetime_value: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., date_value: _Optional[_Union[_date_pb2.Date, _Mapping]]=..., time_value: _Optional[_Union[_time_pb2.Time, _Mapping]]=..., file_value: _Optional[_Union[FileValue, _Mapping]]=..., dictionary_value: _Optional[_Union[DictionaryValue, _Mapping]]=..., list_value: _Optional[_Union[ListValue, _Mapping]]=..., opaque_value: _Optional[_Union[OpaqueValue, _Mapping]]=..., table_value: _Optional[_Union[TableValue, _Mapping]]=..., sensitive_value: _Optional[_Union[SensitiveValue, _Mapping]]=...) -> None:
        ...

class DictionaryValue(_message.Message):
    __slots__ = ('fields', 'is_a')
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    IS_A_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.RepeatedCompositeFieldContainer[DictionaryValueField]
    is_a: _containers.RepeatedCompositeFieldContainer[_noun_phrase_pb2.NounPhrase]

    def __init__(self, fields: _Optional[_Iterable[_Union[DictionaryValueField, _Mapping]]]=..., is_a: _Optional[_Iterable[_Union[_noun_phrase_pb2.NounPhrase, _Mapping]]]=...) -> None:
        ...

class DictionaryValueField(_message.Message):
    __slots__ = ('key', 'value')
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: Value

    def __init__(self, key: _Optional[str]=..., value: _Optional[_Union[Value, _Mapping]]=...) -> None:
        ...

class ListValue(_message.Message):
    __slots__ = ('values',)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[Value]

    def __init__(self, values: _Optional[_Iterable[_Union[Value, _Mapping]]]=...) -> None:
        ...

class FileValue(_message.Message):
    __slots__ = ('remote', 'inline')
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    INLINE_FIELD_NUMBER: _ClassVar[int]
    remote: str
    inline: File

    def __init__(self, remote: _Optional[str]=..., inline: _Optional[_Union[File, _Mapping]]=...) -> None:
        ...

class File(_message.Message):
    __slots__ = ('file_name', 'content')
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    content: bytes

    def __init__(self, file_name: _Optional[str]=..., content: _Optional[bytes]=...) -> None:
        ...

class OpaqueValue(_message.Message):
    __slots__ = ('content', 'is_a')
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    IS_A_FIELD_NUMBER: _ClassVar[int]
    content: bytes
    is_a: _containers.RepeatedCompositeFieldContainer[_noun_phrase_pb2.NounPhrase]

    def __init__(self, content: _Optional[bytes]=..., is_a: _Optional[_Iterable[_Union[_noun_phrase_pb2.NounPhrase, _Mapping]]]=...) -> None:
        ...

class SensitiveValue(_message.Message):
    __slots__ = ('value',)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: Value

    def __init__(self, value: _Optional[_Union[Value, _Mapping]]=...) -> None:
        ...

class TableValue(_message.Message):
    __slots__ = ('remote', 'inline')
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    INLINE_FIELD_NUMBER: _ClassVar[int]
    remote: str
    inline: Table

    def __init__(self, remote: _Optional[str]=..., inline: _Optional[_Union[Table, _Mapping]]=...) -> None:
        ...

class Table(_message.Message):
    __slots__ = ('columns',)
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    columns: _containers.RepeatedCompositeFieldContainer[Column]

    def __init__(self, columns: _Optional[_Iterable[_Union[Column, _Mapping]]]=...) -> None:
        ...

class Column(_message.Message):
    __slots__ = ('values', 'name')
    VALUES_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[Value]
    name: str

    def __init__(self, values: _Optional[_Iterable[_Union[Value, _Mapping]]]=..., name: _Optional[str]=...) -> None:
        ...