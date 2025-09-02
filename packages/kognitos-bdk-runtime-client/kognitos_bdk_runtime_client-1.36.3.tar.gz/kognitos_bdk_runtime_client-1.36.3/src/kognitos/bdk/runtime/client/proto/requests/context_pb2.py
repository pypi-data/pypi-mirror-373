"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16requests/context.proto\x12\x08protocol"\xaf\x02\n\x07Context\x12\x1e\n\x08trace_id\x18\x01 \x01(\x04H\x00R\x07traceId\x88\x01\x01\x12\x1c\n\x07span_id\x18\x02 \x01(\x04H\x01R\x06spanId\x88\x01\x01\x12 \n\tworker_id\x18\x03 \x01(\tH\x02R\x08workerId\x88\x01\x01\x12(\n\rdepartment_id\x18\x04 \x01(\tH\x03R\x0cdepartmentId\x88\x01\x01\x12&\n\x0cknowledge_id\x18\x05 \x01(\tH\x04R\x0bknowledgeId\x88\x01\x01\x12\x1c\n\x07line_id\x18\x06 \x01(\tH\x05R\x06lineId\x88\x01\x01B\x0b\n\t_trace_idB\n\n\x08_span_idB\x0c\n\n_worker_idB\x10\n\x0e_department_idB\x0f\n\r_knowledge_idB\n\n\x08_line_idB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'requests.context_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_CONTEXT']._serialized_start = 37
    _globals['_CONTEXT']._serialized_end = 340