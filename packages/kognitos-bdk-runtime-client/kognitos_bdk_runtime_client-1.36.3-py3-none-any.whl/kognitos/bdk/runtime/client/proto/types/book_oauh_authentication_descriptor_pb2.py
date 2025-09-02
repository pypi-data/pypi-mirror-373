"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import oauth_argument_descriptor_pb2 as types_dot_oauth__argument__descriptor__pb2
from ..types import oauth_flow_pb2 as types_dot_oauth__flow__pb2
from ..types import oauth_provider_pb2 as types_dot_oauth__provider__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n/types/book_oauh_authentication_descriptor.proto\x12\x08protocol\x1a%types/oauth_argument_descriptor.proto\x1a\x16types/oauth_flow.proto\x1a\x1atypes/oauth_provider.proto"\xd4\x02\n!BookOAuthAuthenticationDescriptor\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x123\n\x08provider\x18\x02 \x01(\x0e2\x17.protocol.OAuthProviderR\x08provider\x12)\n\x05flows\x18\x03 \x03(\x0e2\x13.protocol.OAuthFlowR\x05flows\x12-\n\x12authorize_endpoint\x18\x04 \x01(\tR\x11authorizeEndpoint\x12%\n\x0etoken_endpoint\x18\x05 \x01(\tR\rtokenEndpoint\x12\x14\n\x05scope\x18\x06 \x03(\tR\x05scope\x12\x12\n\x04name\x18\x07 \x01(\tR\x04name\x12?\n\targuments\x18\x08 \x03(\x0b2!.protocol.OAuthArgumentDescriptorR\targumentsB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.book_oauh_authentication_descriptor_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_BOOKOAUTHAUTHENTICATIONDESCRIPTOR']._serialized_start = 153
    _globals['_BOOKOAUTHAUTHENTICATIONDESCRIPTOR']._serialized_end = 493