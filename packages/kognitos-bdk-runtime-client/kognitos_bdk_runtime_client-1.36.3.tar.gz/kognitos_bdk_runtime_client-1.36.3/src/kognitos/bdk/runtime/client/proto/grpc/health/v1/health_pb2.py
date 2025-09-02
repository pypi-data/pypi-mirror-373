"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bgrpc/health/v1/health.proto\x12\x0egrpc.health.v1".\n\x12HealthCheckRequest\x12\x18\n\x07service\x18\x01 \x01(\tR\x07service"\xb1\x01\n\x13HealthCheckResponse\x12I\n\x06status\x18\x01 \x01(\x0e21.grpc.health.v1.HealthCheckResponse.ServingStatusR\x06status"O\n\rServingStatus\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0b\n\x07SERVING\x10\x01\x12\x0f\n\x0bNOT_SERVING\x10\x02\x12\x13\n\x0fSERVICE_UNKNOWN\x10\x03"\x13\n\x11HealthListRequest"\xc4\x01\n\x12HealthListResponse\x12L\n\x08statuses\x18\x01 \x03(\x0b20.grpc.health.v1.HealthListResponse.StatusesEntryR\x08statuses\x1a`\n\rStatusesEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x129\n\x05value\x18\x02 \x01(\x0b2#.grpc.health.v1.HealthCheckResponseR\x05value:\x028\x012\xfd\x01\n\x06Health\x12P\n\x05Check\x12".grpc.health.v1.HealthCheckRequest\x1a#.grpc.health.v1.HealthCheckResponse\x12M\n\x04List\x12!.grpc.health.v1.HealthListRequest\x1a".grpc.health.v1.HealthListResponse\x12R\n\x05Watch\x12".grpc.health.v1.HealthCheckRequest\x1a#.grpc.health.v1.HealthCheckResponse0\x01Bp\n\x11io.grpc.health.v1B\x0bHealthProtoP\x01Z,google.golang.org/grpc/health/grpc_health_v1\xa2\x02\x0cGrpcHealthV1\xaa\x02\x0eGrpc.Health.V1b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'grpc.health.v1.health_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x11io.grpc.health.v1B\x0bHealthProtoP\x01Z,google.golang.org/grpc/health/grpc_health_v1\xa2\x02\x0cGrpcHealthV1\xaa\x02\x0eGrpc.Health.V1'
    _globals['_HEALTHLISTRESPONSE_STATUSESENTRY']._options = None
    _globals['_HEALTHLISTRESPONSE_STATUSESENTRY']._serialized_options = b'8\x01'
    _globals['_HEALTHCHECKREQUEST']._serialized_start = 47
    _globals['_HEALTHCHECKREQUEST']._serialized_end = 93
    _globals['_HEALTHCHECKRESPONSE']._serialized_start = 96
    _globals['_HEALTHCHECKRESPONSE']._serialized_end = 273
    _globals['_HEALTHCHECKRESPONSE_SERVINGSTATUS']._serialized_start = 194
    _globals['_HEALTHCHECKRESPONSE_SERVINGSTATUS']._serialized_end = 273
    _globals['_HEALTHLISTREQUEST']._serialized_start = 275
    _globals['_HEALTHLISTREQUEST']._serialized_end = 294
    _globals['_HEALTHLISTRESPONSE']._serialized_start = 297
    _globals['_HEALTHLISTRESPONSE']._serialized_end = 493
    _globals['_HEALTHLISTRESPONSE_STATUSESENTRY']._serialized_start = 397
    _globals['_HEALTHLISTRESPONSE_STATUSESENTRY']._serialized_end = 493
    _globals['_HEALTH']._serialized_start = 496
    _globals['_HEALTH']._serialized_end = 749