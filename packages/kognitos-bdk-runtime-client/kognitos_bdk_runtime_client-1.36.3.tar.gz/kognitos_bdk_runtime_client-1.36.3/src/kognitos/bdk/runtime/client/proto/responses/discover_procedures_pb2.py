"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import book_procedure_descriptor_pb2 as types_dot_book__procedure__descriptor__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#responses/discover_procedures.proto\x12\x08protocol\x1a%types/book_procedure_descriptor.proto"_\n\x1aDiscoverProceduresResponse\x12A\n\nprocedures\x18\x01 \x03(\x0b2!.protocol.BookProcedureDescriptorR\nproceduresB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.discover_procedures_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_DISCOVERPROCEDURESRESPONSE']._serialized_start = 88
    _globals['_DISCOVERPROCEDURESRESPONSE']._serialized_end = 183