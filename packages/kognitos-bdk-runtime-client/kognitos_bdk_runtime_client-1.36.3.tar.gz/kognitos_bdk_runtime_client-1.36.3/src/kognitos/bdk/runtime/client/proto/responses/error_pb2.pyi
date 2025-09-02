from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class ErrorKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ErrorKindInternal: _ClassVar[ErrorKind]
    ErrorKindNotFound: _ClassVar[ErrorKind]
    ErrorKindNotSupported: _ClassVar[ErrorKind]
    ErrorKindMissing: _ClassVar[ErrorKind]
    ErrorKindInvalidValue: _ClassVar[ErrorKind]
    ErrorKindHTTP: _ClassVar[ErrorKind]
    ErrorKindRateLimited: _ClassVar[ErrorKind]
    ErrorKindAccessDenied: _ClassVar[ErrorKind]
    ErrorKindTypeMismatch: _ClassVar[ErrorKind]
    ErrorKindTLS: _ClassVar[ErrorKind]
    ErrorKindAuthenticationRequired: _ClassVar[ErrorKind]
    ErrorKindDeserializationError: _ClassVar[ErrorKind]
ErrorKindInternal: ErrorKind
ErrorKindNotFound: ErrorKind
ErrorKindNotSupported: ErrorKind
ErrorKindMissing: ErrorKind
ErrorKindInvalidValue: ErrorKind
ErrorKindHTTP: ErrorKind
ErrorKindRateLimited: ErrorKind
ErrorKindAccessDenied: ErrorKind
ErrorKindTypeMismatch: ErrorKind
ErrorKindTLS: ErrorKind
ErrorKindAuthenticationRequired: ErrorKind
ErrorKindDeserializationError: ErrorKind

class Error(_message.Message):
    __slots__ = ('kind', 'message', 'extra')

    class ExtraEntry(_message.Message):
        __slots__ = ('key', 'value')
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str

        def __init__(self, key: _Optional[str]=..., value: _Optional[str]=...) -> None:
            ...
    KIND_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    kind: ErrorKind
    message: str
    extra: _containers.ScalarMap[str, str]

    def __init__(self, kind: _Optional[_Union[ErrorKind, str]]=..., message: _Optional[str]=..., extra: _Optional[_Mapping[str, str]]=...) -> None:
        ...