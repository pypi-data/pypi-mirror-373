"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from ..types import concept_type_pb2 as types_dot_concept__type__pb2
from ..types import date_pb2 as types_dot_date__pb2
from ..types import noun_phrase_pb2 as types_dot_noun__phrase__pb2
from ..types import time_pb2 as types_dot_time__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11types/value.proto\x12\x08protocol\x1a\x1cgoogle/protobuf/struct.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x18types/concept_type.proto\x1a\x10types/date.proto\x1a\x17types/noun_phrase.proto\x1a\x10types/time.proto"\xa0\x06\n\x05Value\x12;\n\nnull_value\x18\x01 \x01(\x0e2\x1a.google.protobuf.NullValueH\x00R\tnullValue\x12A\n\x10conceptual_value\x18\x02 \x01(\x0b2\x14.protocol.NounPhraseH\x00R\x0fconceptualValue\x12\x1f\n\ntext_value\x18\x03 \x01(\tH\x00R\ttextValue\x12#\n\x0cnumber_value\x18\x04 \x01(\x01H\x00R\x0bnumberValue\x12%\n\rboolean_value\x18\x05 \x01(\x08H\x00R\x0cbooleanValue\x12C\n\x0edatetime_value\x18\x06 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00R\rdatetimeValue\x12/\n\ndate_value\x18\x07 \x01(\x0b2\x0e.protocol.DateH\x00R\tdateValue\x12/\n\ntime_value\x18\x08 \x01(\x0b2\x0e.protocol.TimeH\x00R\ttimeValue\x124\n\nfile_value\x18\t \x01(\x0b2\x13.protocol.FileValueH\x00R\tfileValue\x12F\n\x10dictionary_value\x18\n \x01(\x0b2\x19.protocol.DictionaryValueH\x00R\x0fdictionaryValue\x124\n\nlist_value\x18\x0b \x01(\x0b2\x13.protocol.ListValueH\x00R\tlistValue\x12:\n\x0copaque_value\x18\x0c \x01(\x0b2\x15.protocol.OpaqueValueH\x00R\x0bopaqueValue\x127\n\x0btable_value\x18\r \x01(\x0b2\x14.protocol.TableValueH\x00R\ntableValue\x12C\n\x0fsensitive_value\x18\x0e \x01(\x0b2\x18.protocol.SensitiveValueH\x00R\x0esensitiveValueB\x15\n\x13value_discriminator"r\n\x0fDictionaryValue\x126\n\x06fields\x18\x01 \x03(\x0b2\x1e.protocol.DictionaryValueFieldR\x06fields\x12\'\n\x04is_a\x18\x02 \x03(\x0b2\x14.protocol.NounPhraseR\x03isA"O\n\x14DictionaryValueField\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12%\n\x05value\x18\x02 \x01(\x0b2\x0f.protocol.ValueR\x05value"4\n\tListValue\x12\'\n\x06values\x18\x01 \x03(\x0b2\x0f.protocol.ValueR\x06values"`\n\tFileValue\x12\x18\n\x06remote\x18\x01 \x01(\tH\x00R\x06remote\x12(\n\x06inline\x18\x02 \x01(\x0b2\x0e.protocol.FileH\x00R\x06inlineB\x0f\n\rinline_remote"=\n\x04File\x12\x1b\n\tfile_name\x18\x01 \x01(\tR\x08fileName\x12\x18\n\x07content\x18\x02 \x01(\x0cR\x07content"P\n\x0bOpaqueValue\x12\x18\n\x07content\x18\x01 \x01(\x0cR\x07content\x12\'\n\x04is_a\x18\x02 \x03(\x0b2\x14.protocol.NounPhraseR\x03isA"7\n\x0eSensitiveValue\x12%\n\x05value\x18\x01 \x01(\x0b2\x0f.protocol.ValueR\x05value"b\n\nTableValue\x12\x18\n\x06remote\x18\x01 \x01(\tH\x00R\x06remote\x12)\n\x06inline\x18\x02 \x01(\x0b2\x0f.protocol.TableH\x00R\x06inlineB\x0f\n\rinline_remote"3\n\x05Table\x12*\n\x07columns\x18\x01 \x03(\x0b2\x10.protocol.ColumnR\x07columns"E\n\x06Column\x12\'\n\x06values\x18\x01 \x03(\x0b2\x0f.protocol.ValueR\x06values\x12\x12\n\x04name\x18\x02 \x01(\tR\x04nameB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.value_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_VALUE']._serialized_start = 182
    _globals['_VALUE']._serialized_end = 982
    _globals['_DICTIONARYVALUE']._serialized_start = 984
    _globals['_DICTIONARYVALUE']._serialized_end = 1098
    _globals['_DICTIONARYVALUEFIELD']._serialized_start = 1100
    _globals['_DICTIONARYVALUEFIELD']._serialized_end = 1179
    _globals['_LISTVALUE']._serialized_start = 1181
    _globals['_LISTVALUE']._serialized_end = 1233
    _globals['_FILEVALUE']._serialized_start = 1235
    _globals['_FILEVALUE']._serialized_end = 1331
    _globals['_FILE']._serialized_start = 1333
    _globals['_FILE']._serialized_end = 1394
    _globals['_OPAQUEVALUE']._serialized_start = 1396
    _globals['_OPAQUEVALUE']._serialized_end = 1476
    _globals['_SENSITIVEVALUE']._serialized_start = 1478
    _globals['_SENSITIVEVALUE']._serialized_end = 1533
    _globals['_TABLEVALUE']._serialized_start = 1535
    _globals['_TABLEVALUE']._serialized_end = 1633
    _globals['_TABLE']._serialized_start = 1635
    _globals['_TABLE']._serialized_end = 1686
    _globals['_COLUMN']._serialized_start = 1688
    _globals['_COLUMN']._serialized_end = 1757