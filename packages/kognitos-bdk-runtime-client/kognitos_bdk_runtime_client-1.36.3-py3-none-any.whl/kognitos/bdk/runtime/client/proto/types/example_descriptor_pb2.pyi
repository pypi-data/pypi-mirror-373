from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional
DESCRIPTOR: _descriptor.FileDescriptor

class ExampleDescriptor(_message.Message):
    __slots__ = ('description', 'snippet')
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SNIPPET_FIELD_NUMBER: _ClassVar[int]
    description: str
    snippet: str

    def __init__(self, description: _Optional[str]=..., snippet: _Optional[str]=...) -> None:
        ...