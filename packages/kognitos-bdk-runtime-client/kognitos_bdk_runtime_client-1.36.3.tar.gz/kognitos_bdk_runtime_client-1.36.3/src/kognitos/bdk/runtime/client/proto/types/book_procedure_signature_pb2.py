"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import noun_phrase_pb2 as types_dot_noun__phrase__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$types/book_procedure_signature.proto\x12\x08protocol\x1a\x17types/noun_phrase.proto"\xf3\x02\n\x16BookProcedureSignature\x12\x18\n\x07english\x18\x01 \x01(\tR\x07english\x12\x14\n\x05verbs\x18\x02 \x03(\tR\x05verbs\x122\n\x06object\x18\x03 \x01(\x0b2\x15.protocol.NounPhrasesH\x00R\x06object\x88\x01\x01\x12%\n\x0bpreposition\x18\x04 \x01(\tH\x01R\x0bpreposition\x88\x01\x01\x122\n\x06target\x18\x05 \x01(\x0b2\x15.protocol.NounPhrasesH\x02R\x06target\x88\x01\x01\x12/\n\x07outputs\x18\x06 \x03(\x0b2\x15.protocol.NounPhrasesR\x07outputs\x12 \n\x0cis_read_only\x18\x07 \x01(\x08R\nisReadOnly\x12!\n\x0cproper_nouns\x18\x08 \x03(\tR\x0bproperNounsB\t\n\x07_objectB\x0e\n\x0c_prepositionB\t\n\x07_targetB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.book_procedure_signature_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_BOOKPROCEDURESIGNATURE']._serialized_start = 76
    _globals['_BOOKPROCEDURESIGNATURE']._serialized_end = 447