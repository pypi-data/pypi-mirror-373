# pylint: disable=no-name-in-module
from datetime import timedelta, timezone

import google.protobuf.timestamp_pb2

from ..proto.types.date_pb2 import Date as ProtoDate
from ..proto.types.time_pb2 import Time as ProtoTime
from ..proto.types.value_pb2 import DictionaryValue as ProtoDict
from ..proto.types.value_pb2 import FileValue as ProtoFileValue
from ..proto.types.value_pb2 import ListValue as ProtoList
from ..proto.types.value_pb2 import OpaqueValue as ProtoOpaqueValue
from ..proto.types.value_pb2 import SensitiveValue as ProtoSensitive
from ..proto.types.value_pb2 import TableValue as ProtoTableValue
from ..proto.types.value_pb2 import Value as ProtoValue
from ..value import (BooleanValue, Column, DatetimeValue, DateValue,
                     DictionaryValue, File, NullValue, NumberValue,
                     OpaqueValue, RemoteFile, RemoteTable, SensitiveValue,
                     Table, TextValue, TimeValue, Value)
from . import noun_phrase as noun_phrase_mapper


def _nanos_to_micros(nanos: int) -> int:
    return nanos // 1000


def _convert_timestamp(
    proto_timestamp: google.protobuf.timestamp_pb2.Timestamp,  # pylint: disable=no-member
) -> DatetimeValue:
    datetime = DatetimeValue.fromtimestamp(proto_timestamp.seconds, tz=timezone.utc)

    return datetime + timedelta(microseconds=_nanos_to_micros(proto_timestamp.nanos))


def _convert_date(proto_date: ProtoDate):
    return DateValue(year=proto_date.year, month=proto_date.month, day=proto_date.day)


def _convert_time(proto_time: ProtoTime):
    return TimeValue(
        hour=proto_time.hours,
        minute=proto_time.minutes,
        second=proto_time.seconds,
        microsecond=_nanos_to_micros(proto_time.nanos),
    )


def _convert_list(proto_list: ProtoList):
    return list(map(map_value, proto_list.values))


def _convert_sensitive(proto_sensitive: ProtoSensitive):
    return SensitiveValue(map_value(proto_sensitive.value))


def _convert_dictionary(proto_dict: ProtoDict):
    return DictionaryValue(
        value={f.key: map_value(f.value) for f in proto_dict.fields},
        is_a=[noun_phrase_mapper.map_noun_phrase(is_a) for is_a in proto_dict.is_a],
    )


def _convert_file(proto_file: ProtoFileValue):
    file_type = proto_file.WhichOneof("inline_remote")

    if file_type == "remote":
        return RemoteFile(url=proto_file.remote)

    if file_type == "inline":
        return File(
            filename=proto_file.inline.file_name, content=proto_file.inline.content
        )

    raise NotImplementedError(f"Could not map file value `{proto_file}`")


def _convert_opaque(proto_opaque: ProtoOpaqueValue):
    return OpaqueValue(
        is_a=[noun_phrase_mapper.map_noun_phrase(is_a) for is_a in proto_opaque.is_a],
        value=proto_opaque.content,
    )


def _convert_table(proto_table: ProtoTableValue):
    proto_table_type = proto_table.WhichOneof("inline_remote")

    if proto_table_type == "inline":
        return Table(
            columns=[
                Column(name=c.name, values=[map_value(val) for val in c.values])
                for c in proto_table.inline.columns
            ],
        )

    if proto_table_type == "remote":
        return RemoteTable(url=proto_table.remote)

    raise NotImplementedError(f"Could not map table value `{proto_table}`")


def map_value(value: ProtoValue) -> Value:
    value_type = value.WhichOneof("value_discriminator")

    if not value_type:
        return None

    value_type_mappings = {
        "conceptual_value": noun_phrase_mapper.map_noun_phrase,
        "number_value": NumberValue,
        "null_value": lambda v: NullValue(),
        "text_value": TextValue,
        "boolean_value": BooleanValue,
        "opaque_value": _convert_opaque,
        "datetime_value": _convert_timestamp,
        "date_value": _convert_date,
        "time_value": _convert_time,
        "list_value": _convert_list,
        "dictionary_value": _convert_dictionary,
        "file_value": _convert_file,
        "table_value": _convert_table,
        "sensitive_value": _convert_sensitive,
    }

    if value_type not in value_type_mappings:
        raise NotImplementedError(f"Could not map value `{value}`")

    return value_type_mappings[value_type](getattr(value, value_type))


def dict_cast(value: dict):
    return DictionaryValue(
        value=value,
        is_a=[],
    )
