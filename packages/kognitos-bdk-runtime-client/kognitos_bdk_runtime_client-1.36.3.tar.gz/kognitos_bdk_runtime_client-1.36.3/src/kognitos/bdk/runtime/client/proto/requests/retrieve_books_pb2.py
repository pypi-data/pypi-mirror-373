"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..common.pagination import pagination_pb2 as common_dot_pagination_dot_pagination__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1drequests/retrieve_books.proto\x12\x08protocol\x1a"common/pagination/pagination.proto"a\n\x14RetrieveBooksRequest\x12I\n\npagination\x18\x01 \x01(\x0b2).common.pagination.TokenPaginationRequestR\npaginationB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'requests.retrieve_books_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_RETRIEVEBOOKSREQUEST']._serialized_start = 79
    _globals['_RETRIEVEBOOKSREQUEST']._serialized_end = 176