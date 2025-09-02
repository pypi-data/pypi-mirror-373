from types import book_descriptor_pb2 as _book_descriptor_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class RetrieveBookResponse(_message.Message):
    __slots__ = ('book',)
    BOOK_FIELD_NUMBER: _ClassVar[int]
    book: _book_descriptor_pb2.BookDescriptor

    def __init__(self, book: _Optional[_Union[_book_descriptor_pb2.BookDescriptor, _Mapping]]=...) -> None:
        ...