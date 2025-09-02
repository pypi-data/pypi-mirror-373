from types import discoverable_pb2 as _discoverable_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class RetrieveDiscoverablesResponse(_message.Message):
    __slots__ = ('discoverables',)
    DISCOVERABLES_FIELD_NUMBER: _ClassVar[int]
    discoverables: _containers.RepeatedCompositeFieldContainer[_discoverable_pb2.Discoverable]

    def __init__(self, discoverables: _Optional[_Iterable[_Union[_discoverable_pb2.Discoverable, _Mapping]]]=...) -> None:
        ...