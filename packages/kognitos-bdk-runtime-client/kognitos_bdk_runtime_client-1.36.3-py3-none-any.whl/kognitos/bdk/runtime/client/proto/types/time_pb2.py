"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10types/time.proto\x12\x08protocol"f\n\x04Time\x12\x14\n\x05hours\x18\x01 \x01(\x05R\x05hours\x12\x18\n\x07minutes\x18\x02 \x01(\x05R\x07minutes\x12\x18\n\x07seconds\x18\x03 \x01(\x05R\x07seconds\x12\x14\n\x05nanos\x18\x04 \x01(\x05R\x05nanosB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.time_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_TIME']._serialized_start = 30
    _globals['_TIME']._serialized_end = 132