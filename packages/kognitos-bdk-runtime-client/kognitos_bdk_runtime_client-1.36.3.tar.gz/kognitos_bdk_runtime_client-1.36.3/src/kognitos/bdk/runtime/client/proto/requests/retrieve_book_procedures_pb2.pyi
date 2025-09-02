from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional
DESCRIPTOR: _descriptor.FileDescriptor

class RetrieveBookProceduresRequest(_message.Message):
    __slots__ = ('name', 'version', 'include_connect')
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_CONNECT_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    include_connect: bool

    def __init__(self, name: _Optional[str]=..., version: _Optional[str]=..., include_connect: bool=...) -> None:
        ...