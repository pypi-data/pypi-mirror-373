"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import value_pb2 as types_dot_value__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1drequests/authentication.proto\x12\x08protocol\x1a\x11types/value.proto"\x97\x01\n\x0eAuthentication\x12+\n\x11authentication_id\x18\x03 \x01(\tR\x10authenticationId\x12X\n\x1aauthentication_credentials\x18\x04 \x03(\x0b2\x19.protocol.CredentialValueR\x19authenticationCredentials"H\n\x0fCredentialValue\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12%\n\x05value\x18\x02 \x01(\x0b2\x0f.protocol.ValueR\x05valueB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'requests.authentication_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_AUTHENTICATION']._serialized_start = 63
    _globals['_AUTHENTICATION']._serialized_end = 214
    _globals['_CREDENTIALVALUE']._serialized_start = 216
    _globals['_CREDENTIALVALUE']._serialized_end = 288