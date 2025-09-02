"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..common.pagination import pagination_pb2 as common_dot_pagination_dot_pagination__pb2
from ..types import book_descriptor_pb2 as types_dot_book__descriptor__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eresponses/retrieve_books.proto\x12\x08protocol\x1a"common/pagination/pagination.proto\x1a\x1btypes/book_descriptor.proto"\x93\x01\n\x15RetrieveBooksResponse\x12.\n\x05books\x18\x01 \x03(\x0b2\x18.protocol.BookDescriptorR\x05books\x12J\n\npagination\x18\x02 \x01(\x0b2*.common.pagination.TokenPaginationResponseR\npaginationB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.retrieve_books_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_RETRIEVEBOOKSRESPONSE']._serialized_start = 110
    _globals['_RETRIEVEBOOKSRESPONSE']._serialized_end = 257