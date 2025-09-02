from common.pagination import pagination_pb2 as _pagination_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class RetrieveBooksRequest(_message.Message):
    __slots__ = ('pagination',)
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    pagination: _pagination_pb2.TokenPaginationRequest

    def __init__(self, pagination: _Optional[_Union[_pagination_pb2.TokenPaginationRequest, _Mapping]]=...) -> None:
        ...