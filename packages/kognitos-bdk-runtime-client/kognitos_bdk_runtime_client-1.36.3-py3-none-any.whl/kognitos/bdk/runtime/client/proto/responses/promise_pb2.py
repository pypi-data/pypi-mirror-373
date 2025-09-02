"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import promise_pb2 as types_dot_promise__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17responses/promise.proto\x12\x08protocol\x1a\x13types/promise.proto">\n\x0fPromiseResponse\x12+\n\x07promise\x18\x01 \x01(\x0b2\x11.protocol.PromiseR\x07promiseB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.promise_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_PROMISERESPONSE']._serialized_start = 58
    _globals['_PROMISERESPONSE']._serialized_end = 120