"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16requests/offload.proto\x12\x08protocol"L\n\x07Offload\x12(\n\x03aws\x18\x01 \x01(\x0b2\x14.protocol.AWSOffloadH\x00R\x03awsB\x17\n\x15offload_discriminator"\xf9\x01\n\nAWSOffload\x12\x1d\n\naccess_key\x18\x01 \x01(\tR\taccessKey\x12\x1d\n\nsecret_key\x18\x02 \x01(\tR\tsecretKey\x12#\n\rsession_token\x18\x03 \x01(\tR\x0csessionToken\x12\x16\n\x06region\x18\x04 \x01(\tR\x06region\x12\x16\n\x06bucket\x18\x05 \x01(\tR\x06bucket\x12\x1f\n\x0bfolder_name\x18\x06 \x01(\tR\nfolderName\x12&\n\x0cendpoint_url\x18\x07 \x01(\tH\x00R\x0bendpointUrl\x88\x01\x01B\x0f\n\r_endpoint_urlB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'requests.offload_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_OFFLOAD']._serialized_start = 36
    _globals['_OFFLOAD']._serialized_end = 112
    _globals['_AWSOFFLOAD']._serialized_start = 115
    _globals['_AWSOFFLOAD']._serialized_end = 364