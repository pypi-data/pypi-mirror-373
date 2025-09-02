"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17types/noun_phrase.proto\x12\x08protocol">\n\nNounPhrase\x12\x1c\n\tmodifiers\x18\x01 \x03(\tR\tmodifiers\x12\x12\n\x04head\x18\x02 \x01(\tR\x04head"F\n\x0bNounPhrases\x127\n\x0cnoun_phrases\x18\x01 \x03(\x0b2\x14.protocol.NounPhraseR\x0bnounPhrasesB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.noun_phrase_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_NOUNPHRASE']._serialized_start = 37
    _globals['_NOUNPHRASE']._serialized_end = 99
    _globals['_NOUNPHRASES']._serialized_start = 101
    _globals['_NOUNPHRASES']._serialized_end = 171