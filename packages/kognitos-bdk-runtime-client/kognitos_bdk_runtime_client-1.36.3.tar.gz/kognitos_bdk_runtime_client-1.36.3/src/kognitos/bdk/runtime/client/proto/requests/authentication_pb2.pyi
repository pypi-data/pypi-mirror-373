from types import value_pb2 as _value_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Authentication(_message.Message):
    __slots__ = ('authentication_id', 'authentication_credentials')
    AUTHENTICATION_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    authentication_id: str
    authentication_credentials: _containers.RepeatedCompositeFieldContainer[CredentialValue]

    def __init__(self, authentication_id: _Optional[str]=..., authentication_credentials: _Optional[_Iterable[_Union[CredentialValue, _Mapping]]]=...) -> None:
        ...

class CredentialValue(_message.Message):
    __slots__ = ('id', 'value')
    ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: str
    value: _value_pb2.Value

    def __init__(self, id: _Optional[str]=..., value: _Optional[_Union[_value_pb2.Value, _Mapping]]=...) -> None:
        ...