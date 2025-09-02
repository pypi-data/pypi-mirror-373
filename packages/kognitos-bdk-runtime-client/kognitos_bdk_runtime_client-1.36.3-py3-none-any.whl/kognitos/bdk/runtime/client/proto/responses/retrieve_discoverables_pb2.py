"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import discoverable_pb2 as types_dot_discoverable__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n&responses/retrieve_discoverables.proto\x12\x08protocol\x1a\x18types/discoverable.proto"]\n\x1dRetrieveDiscoverablesResponse\x12<\n\rdiscoverables\x18\x01 \x03(\x0b2\x16.protocol.DiscoverableR\rdiscoverablesB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.retrieve_discoverables_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_RETRIEVEDISCOVERABLESRESPONSE']._serialized_start = 78
    _globals['_RETRIEVEDISCOVERABLESRESPONSE']._serialized_end = 171