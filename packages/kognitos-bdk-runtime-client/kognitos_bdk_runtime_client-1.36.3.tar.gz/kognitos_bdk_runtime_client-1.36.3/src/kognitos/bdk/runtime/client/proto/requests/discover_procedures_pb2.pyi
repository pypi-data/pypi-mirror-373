from requests import authentication_pb2 as _authentication_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class DiscoverProceduresRequest(_message.Message):
    __slots__ = ('name', 'version', 'authentication', 'what')
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_FIELD_NUMBER: _ClassVar[int]
    WHAT_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    authentication: _authentication_pb2.Authentication
    what: _containers.RepeatedScalarFieldContainer[str]

    def __init__(self, name: _Optional[str]=..., version: _Optional[str]=..., authentication: _Optional[_Union[_authentication_pb2.Authentication, _Mapping]]=..., what: _Optional[_Iterable[str]]=...) -> None:
        ...