from types import book_procedure_descriptor_pb2 as _book_procedure_descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class DiscoverProceduresResponse(_message.Message):
    __slots__ = ('procedures',)
    PROCEDURES_FIELD_NUMBER: _ClassVar[int]
    procedures: _containers.RepeatedCompositeFieldContainer[_book_procedure_descriptor_pb2.BookProcedureDescriptor]

    def __init__(self, procedures: _Optional[_Iterable[_Union[_book_procedure_descriptor_pb2.BookProcedureDescriptor, _Mapping]]]=...) -> None:
        ...