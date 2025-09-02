from requests import authentication_pb2 as _authentication_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class TestConnectionRequest(_message.Message):
    __slots__ = ('name', 'version', 'authentication')
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    authentication: _authentication_pb2.Authentication

    def __init__(self, name: _Optional[str]=..., version: _Optional[str]=..., authentication: _Optional[_Union[_authentication_pb2.Authentication, _Mapping]]=...) -> None:
        ...