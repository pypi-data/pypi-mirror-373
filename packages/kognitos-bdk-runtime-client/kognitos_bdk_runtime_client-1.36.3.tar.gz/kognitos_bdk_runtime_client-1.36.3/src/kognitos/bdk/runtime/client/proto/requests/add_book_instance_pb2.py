"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..requests import authentication_pb2 as requests_dot_authentication__pb2
from ..requests import labels_pb2 as requests_dot_labels__pb2
from ..types import config_value_pb2 as types_dot_config__value__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n requests/add_book_instance.proto\x12\x08protocol\x1a\x1drequests/authentication.proto\x1a\x15requests/labels.proto\x1a\x18types/config_value.proto"\xf2\x01\n\x16AddBookInstanceRequest\x12\x1b\n\tbook_name\x18\x01 \x01(\tR\x08bookName\x12!\n\x0cbook_version\x18\x02 \x01(\tR\x0bbookVersion\x12@\n\x0eauthentication\x18\x03 \x01(\x0b2\x18.protocol.AuthenticationR\x0eauthentication\x12-\n\x06config\x18\x04 \x03(\x0b2\x15.protocol.ConfigValueR\x06config\x12\'\n\x06labels\x18\x05 \x03(\x0b2\x0f.protocol.LabelR\x06labelsB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'requests.add_book_instance_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_ADDBOOKINSTANCEREQUEST']._serialized_start = 127
    _globals['_ADDBOOKINSTANCEREQUEST']._serialized_end = 369