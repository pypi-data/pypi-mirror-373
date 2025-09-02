"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from .grpc.health.v1 import health_pb2 as grpc_dot_health_dot_v1_dot_health__pb2
from .requests import request_pb2 as requests_dot_request__pb2
from .responses import response_pb2 as responses_dot_response__pb2
from .services import book_pb2 as services_dot_book__pb2
from .services import library_pb2 as services_dot_library__pb2
from . import version_pb2 as version__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tbci.proto\x12\x08protocol\x1a\x1cgoogle/protobuf/struct.proto\x1a\x1bgrpc/health/v1/health.proto\x1a\x16requests/request.proto\x1a\x18responses/response.proto\x1a\x13services/book.proto\x1a\x16services/library.proto\x1a\rversion.protoB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'bci_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'