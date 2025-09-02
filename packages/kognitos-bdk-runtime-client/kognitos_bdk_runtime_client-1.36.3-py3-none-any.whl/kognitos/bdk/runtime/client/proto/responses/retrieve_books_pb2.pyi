from common.pagination import pagination_pb2 as _pagination_pb2
from types import book_descriptor_pb2 as _book_descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class RetrieveBooksResponse(_message.Message):
    __slots__ = ('books', 'pagination')
    BOOKS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    books: _containers.RepeatedCompositeFieldContainer[_book_descriptor_pb2.BookDescriptor]
    pagination: _pagination_pb2.TokenPaginationResponse

    def __init__(self, books: _Optional[_Iterable[_Union[_book_descriptor_pb2.BookDescriptor, _Mapping]]]=..., pagination: _Optional[_Union[_pagination_pb2.TokenPaginationResponse, _Mapping]]=...) -> None:
        ...