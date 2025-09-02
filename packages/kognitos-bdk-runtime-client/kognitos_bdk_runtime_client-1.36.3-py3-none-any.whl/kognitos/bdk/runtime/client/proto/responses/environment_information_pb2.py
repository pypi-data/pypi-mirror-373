"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'responses/environment_information.proto\x12\x08protocol"\xed\x01\n\x1eEnvironmentInformationResponse\x12\x18\n\x07version\x18\x01 \x01(\tR\x07version\x12!\n\x0cruntime_name\x18\x02 \x01(\tR\x0bruntimeName\x12\'\n\x0fruntime_version\x18\x03 \x01(\tR\x0eruntimeVersion\x120\n\x14bci_protocol_version\x18\x04 \x01(\tR\x12bciProtocolVersion\x12\x1f\n\x0bapi_version\x18\x05 \x01(\tR\napiVersion\x12\x12\n\x04path\x18\x06 \x03(\tR\x04pathB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.environment_information_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_ENVIRONMENTINFORMATIONRESPONSE']._serialized_start = 54
    _globals['_ENVIRONMENTINFORMATIONRESPONSE']._serialized_end = 291