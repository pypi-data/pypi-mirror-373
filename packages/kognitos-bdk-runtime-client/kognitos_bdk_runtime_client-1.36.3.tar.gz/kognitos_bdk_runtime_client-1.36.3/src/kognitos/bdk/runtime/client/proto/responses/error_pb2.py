"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15responses/error.proto\x12\x08protocol"\xb6\x01\n\x05Error\x12\'\n\x04kind\x18\x01 \x01(\x0e2\x13.protocol.ErrorKindR\x04kind\x12\x18\n\x07message\x18\x02 \x01(\tR\x07message\x120\n\x05extra\x18\x03 \x03(\x0b2\x1a.protocol.Error.ExtraEntryR\x05extra\x1a8\n\nExtraEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x14\n\x05value\x18\x02 \x01(\tR\x05value:\x028\x01*\xc2\x02\n\tErrorKind\x12\x15\n\x11ErrorKindInternal\x10\x00\x12\x15\n\x11ErrorKindNotFound\x10\x01\x12\x19\n\x15ErrorKindNotSupported\x10\x02\x12\x14\n\x10ErrorKindMissing\x10\x03\x12\x19\n\x15ErrorKindInvalidValue\x10\x04\x12\x11\n\rErrorKindHTTP\x10\x05\x12\x18\n\x14ErrorKindRateLimited\x10\x06\x12\x19\n\x15ErrorKindAccessDenied\x10\x07\x12\x19\n\x15ErrorKindTypeMismatch\x10\x08\x12\x10\n\x0cErrorKindTLS\x10\t\x12#\n\x1fErrorKindAuthenticationRequired\x10\n\x12!\n\x1dErrorKindDeserializationError\x10\x0bB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.error_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_ERROR_EXTRAENTRY']._options = None
    _globals['_ERROR_EXTRAENTRY']._serialized_options = b'8\x01'
    _globals['_ERRORKIND']._serialized_start = 221
    _globals['_ERRORKIND']._serialized_end = 543
    _globals['_ERROR']._serialized_start = 36
    _globals['_ERROR']._serialized_end = 218
    _globals['_ERROR_EXTRAENTRY']._serialized_start = 162
    _globals['_ERROR_EXTRAENTRY']._serialized_end = 218