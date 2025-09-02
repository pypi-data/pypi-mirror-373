from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional
DESCRIPTOR: _descriptor.FileDescriptor

class EnvironmentInformationResponse(_message.Message):
    __slots__ = ('version', 'runtime_name', 'runtime_version', 'bci_protocol_version', 'api_version', 'path')
    VERSION_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_NAME_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    BCI_PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    API_VERSION_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    version: str
    runtime_name: str
    runtime_version: str
    bci_protocol_version: str
    api_version: str
    path: _containers.RepeatedScalarFieldContainer[str]

    def __init__(self, version: _Optional[str]=..., runtime_name: _Optional[str]=..., runtime_version: _Optional[str]=..., bci_protocol_version: _Optional[str]=..., api_version: _Optional[str]=..., path: _Optional[_Iterable[str]]=...) -> None:
        ...