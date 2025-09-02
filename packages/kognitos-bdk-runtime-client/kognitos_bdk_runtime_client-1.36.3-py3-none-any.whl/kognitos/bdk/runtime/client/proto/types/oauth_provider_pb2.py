"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1atypes/oauth_provider.proto\x12\x08protocol*^\n\rOAuthProvider\x12\x1a\n\x16OAuthProviderMicrosoft\x10\x00\x12\x17\n\x13OAuthProviderGoogle\x10\x01\x12\x18\n\x14OAuthProviderGeneric\x10\x02B\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.oauth_provider_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_OAUTHPROVIDER']._serialized_start = 40
    _globals['_OAUTHPROVIDER']._serialized_end = 134