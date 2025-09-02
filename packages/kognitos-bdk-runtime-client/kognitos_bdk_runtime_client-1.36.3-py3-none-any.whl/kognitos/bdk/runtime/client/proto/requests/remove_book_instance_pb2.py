"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#requests/remove_book_instance.proto\x12\x08protocol"|\n\x19RemoveBookInstanceRequest\x12\x1f\n\x0binstance_id\x18\x01 \x01(\tR\ninstanceId\x12\x1b\n\tbook_name\x18\x02 \x01(\tR\x08bookName\x12!\n\x0cbook_version\x18\x03 \x01(\tR\x0bbookVersionB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'requests.remove_book_instance_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_REMOVEBOOKINSTANCEREQUEST']._serialized_start = 49
    _globals['_REMOVEBOOKINSTANCEREQUEST']._serialized_end = 173