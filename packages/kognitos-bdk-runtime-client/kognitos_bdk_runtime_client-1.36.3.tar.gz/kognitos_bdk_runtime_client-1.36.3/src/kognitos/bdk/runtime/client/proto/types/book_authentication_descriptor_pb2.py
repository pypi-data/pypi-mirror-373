"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import book_custom_authentication_descriptor_pb2 as types_dot_book__custom__authentication__descriptor__pb2
from ..types import book_oauh_authentication_descriptor_pb2 as types_dot_book__oauh__authentication__descriptor__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n*types/book_authentication_descriptor.proto\x12\x08protocol\x1a1types/book_custom_authentication_descriptor.proto\x1a/types/book_oauh_authentication_descriptor.proto"\xcb\x01\n\x1cBookAuthenticationDescriptor\x12F\n\x06custom\x18\x01 \x01(\x0b2,.protocol.BookCustomAuthenticationDescriptorH\x00R\x06custom\x12C\n\x05oauth\x18\x02 \x01(\x0b2+.protocol.BookOAuthAuthenticationDescriptorH\x00R\x05oauthB\x1e\n\x1cauthentication_discriminatorB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.book_authentication_descriptor_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_BOOKAUTHENTICATIONDESCRIPTOR']._serialized_start = 157
    _globals['_BOOKAUTHENTICATIONDESCRIPTOR']._serialized_end = 360