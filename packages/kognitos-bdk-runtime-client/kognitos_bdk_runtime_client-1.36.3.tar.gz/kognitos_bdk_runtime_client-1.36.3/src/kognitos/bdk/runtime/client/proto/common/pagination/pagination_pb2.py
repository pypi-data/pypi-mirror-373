"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n"common/pagination/pagination.proto\x12\x11common.pagination"O\n\x16TokenPaginationRequest\x12\x1f\n\x0bstart_token\x18\x01 \x01(\tR\nstartToken\x12\x14\n\x05count\x18\x02 \x01(\tR\x05count"8\n\x17TokenPaginationResponse\x12\x1d\n\nnext_token\x18\x01 \x01(\tR\tnextToken"i\n\x15PagePaginationRequest\x12\x17\n\x04page\x18\x01 \x01(\rH\x00R\x04page\x88\x01\x01\x12 \n\tpage_size\x18\x02 \x01(\rH\x01R\x08pageSize\x88\x01\x01B\x07\n\x05_pageB\x0c\n\n_page_size"\xa2\x01\n\x16PagePaginationResponse\x12\x19\n\x08has_more\x18\x01 \x01(\x08R\x07hasMore\x12$\n\x0btotal_count\x18\x02 \x01(\rH\x00R\ntotalCount\x88\x01\x01\x12&\n\x0ccurrent_page\x18\x03 \x01(\rH\x01R\x0bcurrentPage\x88\x01\x01B\x0e\n\x0c_total_countB\x0f\n\r_current_pageb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'common.pagination.pagination_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals['_TOKENPAGINATIONREQUEST']._serialized_start = 57
    _globals['_TOKENPAGINATIONREQUEST']._serialized_end = 136
    _globals['_TOKENPAGINATIONRESPONSE']._serialized_start = 138
    _globals['_TOKENPAGINATIONRESPONSE']._serialized_end = 194
    _globals['_PAGEPAGINATIONREQUEST']._serialized_start = 196
    _globals['_PAGEPAGINATIONREQUEST']._serialized_end = 301
    _globals['_PAGEPAGINATIONRESPONSE']._serialized_start = 304
    _globals['_PAGEPAGINATIONRESPONSE']._serialized_end = 466