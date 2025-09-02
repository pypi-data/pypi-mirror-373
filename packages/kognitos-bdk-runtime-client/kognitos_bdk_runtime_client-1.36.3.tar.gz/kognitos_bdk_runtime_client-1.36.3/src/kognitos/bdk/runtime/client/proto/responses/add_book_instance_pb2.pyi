from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional
DESCRIPTOR: _descriptor.FileDescriptor

class AddBookInstanceResponse(_message.Message):
    __slots__ = ('instance_id',)
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    instance_id: str

    def __init__(self, instance_id: _Optional[str]=...) -> None:
        ...