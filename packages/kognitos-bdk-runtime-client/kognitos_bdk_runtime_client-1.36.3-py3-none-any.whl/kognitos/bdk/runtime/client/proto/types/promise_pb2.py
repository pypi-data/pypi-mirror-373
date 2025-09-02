"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import value_pb2 as types_dot_value__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13types/promise.proto\x12\x08protocol\x1a\x11types/value.proto"s\n\x07Promise\x12C\n\x1epromise_resolver_function_name\x18\x01 \x01(\tR\x1bpromiseResolverFunctionName\x12#\n\x04data\x18\x02 \x01(\x0b2\x0f.protocol.ValueR\x04datab\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.promise_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals['_PROMISE']._serialized_start = 52
    _globals['_PROMISE']._serialized_end = 167