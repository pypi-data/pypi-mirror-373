"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import noun_phrase_pb2 as types_dot_noun__phrase__pb2
from ..types import value_pb2 as types_dot_value__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dtypes/answered_question.proto\x12\x08protocol\x1a\x17types/noun_phrase.proto\x1a\x11types/value.proto"u\n\x10AnsweredQuestion\x128\n\x0cnoun_phrases\x18\x01 \x01(\x0b2\x15.protocol.NounPhrasesR\x0bnounPhrases\x12\'\n\x06answer\x18\x02 \x01(\x0b2\x0f.protocol.ValueR\x06answerB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.answered_question_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_ANSWEREDQUESTION']._serialized_start = 87
    _globals['_ANSWEREDQUESTION']._serialized_end = 204