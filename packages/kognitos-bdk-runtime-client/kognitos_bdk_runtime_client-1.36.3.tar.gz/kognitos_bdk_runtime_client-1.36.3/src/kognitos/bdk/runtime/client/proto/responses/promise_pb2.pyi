from types import promise_pb2 as _promise_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class PromiseResponse(_message.Message):
    __slots__ = ('promise',)
    PROMISE_FIELD_NUMBER: _ClassVar[int]
    promise: _promise_pb2.Promise

    def __init__(self, promise: _Optional[_Union[_promise_pb2.Promise, _Mapping]]=...) -> None:
        ...