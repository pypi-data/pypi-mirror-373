"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import book_authentication_descriptor_pb2 as types_dot_book__authentication__descriptor__pb2
from ..types import book_procedure_descriptor_pb2 as types_dot_book__procedure__descriptor__pb2
from ..types import concept_descriptor_pb2 as types_dot_concept__descriptor__pb2
from ..types import noun_phrase_pb2 as types_dot_noun__phrase__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1btypes/book_descriptor.proto\x12\x08protocol\x1a*types/book_authentication_descriptor.proto\x1a%types/book_procedure_descriptor.proto\x1a\x1etypes/concept_descriptor.proto\x1a\x17types/noun_phrase.proto"\xd1\x06\n\x0eBookDescriptor\x12\x12\n\x02id\x18\x01 \x01(\tB\x02\x18\x01R\x02id\x12\x12\n\x04name\x18\x02 \x01(\tR\x04name\x120\n\x11short_description\x18\x03 \x01(\tH\x00R\x10shortDescription\x88\x01\x01\x12.\n\x10long_description\x18\x04 \x01(\tH\x01R\x0flongDescription\x88\x01\x01\x12\x1b\n\x06author\x18\x05 \x01(\tH\x02R\x06author\x88\x01\x01\x12\x12\n\x04icon\x18\x06 \x01(\x0cR\x04icon\x12\x18\n\x07version\x18\x07 \x01(\tR\x07version\x12P\n\x0fauthentications\x18\x08 \x03(\x0b2&.protocol.BookAuthenticationDescriptorR\x0fauthentications\x12C\n\x0econfigurations\x18\t \x03(\x0b2\x1b.protocol.ConceptDescriptorR\x0econfigurations\x12&\n\x0cdisplay_name\x18\n \x01(\tH\x03R\x0bdisplayName\x88\x01\x01\x12\x1f\n\x08endpoint\x18\x0b \x01(\tH\x04R\x08endpoint\x88\x01\x01\x124\n\x13connection_required\x18\x0c \x01(\x08H\x05R\x12connectionRequired\x88\x01\x01\x12.\n\x10discover_capable\x18\r \x01(\x08H\x06R\x0fdiscoverCapable\x88\x01\x01\x12\x12\n\x04tags\x18\x0e \x03(\tR\x04tags\x12C\n\nprocedures\x18\x0f \x03(\x0b2#.protocol.BookProcedureDescriptorV2R\nprocedures\x12:\n\x0bnoun_phrase\x18\x10 \x01(\x0b2\x14.protocol.NounPhraseH\x07R\nnounPhrase\x88\x01\x01B\x14\n\x12_short_descriptionB\x13\n\x11_long_descriptionB\t\n\x07_authorB\x0f\n\r_display_nameB\x0b\n\t_endpointB\x16\n\x14_connection_requiredB\x13\n\x11_discover_capableB\x0e\n\x0c_noun_phraseB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.book_descriptor_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_BOOKDESCRIPTOR'].fields_by_name['id']._options = None
    _globals['_BOOKDESCRIPTOR'].fields_by_name['id']._serialized_options = b'\x18\x01'
    _globals['_BOOKDESCRIPTOR']._serialized_start = 182
    _globals['_BOOKDESCRIPTOR']._serialized_end = 1031