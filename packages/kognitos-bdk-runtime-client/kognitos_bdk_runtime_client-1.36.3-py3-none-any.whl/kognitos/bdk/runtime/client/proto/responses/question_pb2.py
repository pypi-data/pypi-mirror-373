"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import question_pb2 as types_dot_question__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18responses/question.proto\x12\x08protocol\x1a\x14types/question.proto"D\n\x10QuestionResponse\x120\n\tquestions\x18\x01 \x03(\x0b2\x12.protocol.QuestionR\tquestionsB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.question_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_QUESTIONRESPONSE']._serialized_start = 60
    _globals['_QUESTIONRESPONSE']._serialized_end = 128