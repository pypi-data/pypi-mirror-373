from types import value_pb2 as _value_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Promise(_message.Message):
    __slots__ = ('promise_resolver_function_name', 'data')
    PROMISE_RESOLVER_FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    promise_resolver_function_name: str
    data: _value_pb2.Value

    def __init__(self, promise_resolver_function_name: _Optional[str]=..., data: _Optional[_Union[_value_pb2.Value, _Mapping]]=...) -> None:
        ...