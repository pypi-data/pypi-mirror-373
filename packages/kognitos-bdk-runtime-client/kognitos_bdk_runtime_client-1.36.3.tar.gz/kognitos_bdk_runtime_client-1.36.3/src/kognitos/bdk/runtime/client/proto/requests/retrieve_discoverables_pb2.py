"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..requests import authentication_pb2 as requests_dot_authentication__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%requests/retrieve_discoverables.proto\x12\x08protocol\x1a\x1drequests/authentication.proto"\x83\x02\n\x1cRetrieveDiscoverablesRequest\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\x12\x18\n\x07version\x18\x02 \x01(\tR\x07version\x12@\n\x0eauthentication\x18\x03 \x01(\x0b2\x18.protocol.AuthenticationR\x0eauthentication\x12\x1b\n\x06search\x18\x04 \x01(\tH\x00R\x06search\x88\x01\x01\x12\x1b\n\x06offset\x18\x05 \x01(\x04H\x01R\x06offset\x88\x01\x01\x12\x19\n\x05limit\x18\x06 \x01(\x04H\x02R\x05limit\x88\x01\x01B\t\n\x07_searchB\t\n\x07_offsetB\x08\n\x06_limitB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'requests.retrieve_discoverables_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_RETRIEVEDISCOVERABLESREQUEST']._serialized_start = 83
    _globals['_RETRIEVEDISCOVERABLESREQUEST']._serialized_end = 342