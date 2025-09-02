from types import credential_type_pb2 as _credential_type_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class CredentialDescriptor(_message.Message):
    __slots__ = ('id', 'type', 'label', 'visible', 'description')
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: _credential_type_pb2.CredentialType
    label: str
    visible: bool
    description: str

    def __init__(self, id: _Optional[str]=..., type: _Optional[_Union[_credential_type_pb2.CredentialType, str]]=..., label: _Optional[str]=..., visible: bool=..., description: _Optional[str]=...) -> None:
        ...