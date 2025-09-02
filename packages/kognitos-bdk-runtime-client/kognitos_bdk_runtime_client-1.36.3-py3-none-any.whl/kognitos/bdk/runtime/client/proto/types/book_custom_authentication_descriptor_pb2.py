"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import credential_descriptor_pb2 as types_dot_credential__descriptor__pb2
from ..types import noun_phrase_pb2 as types_dot_noun__phrase__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n1types/book_custom_authentication_descriptor.proto\x12\x08protocol\x1a!types/credential_descriptor.proto\x1a\x17types/noun_phrase.proto"\xf8\x01\n"BookCustomAuthenticationDescriptor\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12@\n\x0bcredentials\x18\x02 \x03(\x0b2\x1e.protocol.CredentialDescriptorR\x0bcredentials\x12 \n\x0bdescription\x18\x03 \x01(\tR\x0bdescription\x12\x12\n\x04name\x18\x04 \x01(\tR\x04name\x12:\n\x0bnoun_phrase\x18\x05 \x01(\x0b2\x14.protocol.NounPhraseH\x00R\nnounPhrase\x88\x01\x01B\x0e\n\x0c_noun_phraseB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.book_custom_authentication_descriptor_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_BOOKCUSTOMAUTHENTICATIONDESCRIPTOR']._serialized_start = 124
    _globals['_BOOKCUSTOMAUTHENTICATIONDESCRIPTOR']._serialized_end = 372