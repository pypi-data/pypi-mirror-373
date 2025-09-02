"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..requests import authentication_pb2 as requests_dot_authentication__pb2
from ..requests import offload_pb2 as requests_dot_offload__pb2
from ..types import answered_question_pb2 as types_dot_answered__question__pb2
from ..types import concept_value_pb2 as types_dot_concept__value__pb2
from ..types import promise_pb2 as types_dot_promise__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1erequests/resolve_promise.proto\x12\x08protocol\x1a\x1drequests/authentication.proto\x1a\x16requests/offload.proto\x1a\x1dtypes/answered_question.proto\x1a\x19types/concept_value.proto\x1a\x13types/promise.proto"\xa0\x03\n\x15ResolvePromiseRequest\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\x12\x18\n\x07version\x18\x02 \x01(\tR\x07version\x12@\n\x0eauthentication\x18\x03 \x01(\x0b2\x18.protocol.AuthenticationR\x0eauthentication\x12!\n\x0cprocedure_id\x18\x04 \x01(\tR\x0bprocedureId\x12+\n\x07promise\x18\x05 \x01(\x0b2\x11.protocol.PromiseR\x07promise\x120\n\x07offload\x18\x06 \x01(\x0b2\x11.protocol.OffloadH\x00R\x07offload\x88\x01\x01\x12I\n\x12answered_questions\x18\x07 \x03(\x0b2\x1a.protocol.AnsweredQuestionR\x11answeredQuestions\x12>\n\x0econfigurations\x18\x08 \x03(\x0b2\x16.protocol.ConceptValueR\x0econfigurationsB\n\n\x08_offloadB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'requests.resolve_promise_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_RESOLVEPROMISEREQUEST']._serialized_start = 179
    _globals['_RESOLVEPROMISEREQUEST']._serialized_end = 595