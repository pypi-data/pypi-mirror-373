from typing import Tuple

import google.protobuf.timestamp_pb2
from google.protobuf.struct_pb2 import \
    NULL_VALUE as PROTO_NULL_VALUE  # pylint: disable=no-name-in-module

# pylint: disable=no-name-in-module
from ..proto.types.date_pb2 import Date as ProtoDate
from ..proto.types.noun_phrase_pb2 import NounPhrase as ProtoNounPhrase
from ..proto.types.time_pb2 import Time as ProtoTime
from ..proto.types.value_pb2 import Column as ProtoColumn
from ..proto.types.value_pb2 import DictionaryValue as ProtoDictionaryValue
from ..proto.types.value_pb2 import \
    DictionaryValueField as ProtoDictionaryValueField
from ..proto.types.value_pb2 import File as ProtoFile
from ..proto.types.value_pb2 import FileValue as ProtoFileValue
from ..proto.types.value_pb2 import ListValue as ProtoListValue
from ..proto.types.value_pb2 import OpaqueValue as ProtoOpaqueValue
from ..proto.types.value_pb2 import SensitiveValue as ProtoSensitiveValue
from ..proto.types.value_pb2 import Table as ProtoTable
from ..proto.types.value_pb2 import TableValue as ProtoTableValue
from ..proto.types.value_pb2 import Value as ProtoValue
from ..value import (BooleanValue, ConceptualValue, DatetimeValue, DateValue,
                     DictionaryValue, File, ListValue, NullValue, NumberValue,
                     OpaqueValue, RemoteFile, RemoteTable, SensitiveValue,
                     Table, TextValue, TimeValue, Value)


def _micros_to_nanos(micros: int) -> int:
    return micros * 1000


def _timestamp_to_seconds_and_nanos(datetime: DatetimeValue) -> Tuple[int, int]:
    return int(datetime.timestamp()), _micros_to_nanos(datetime.microsecond)


def map_value(value: Value) -> ProtoValue:
    """Maps a value from bdk-runtime-client domain to proto"""

    if isinstance(value, ConceptualValue):
        return ProtoValue(
            conceptual_value=ProtoNounPhrase(head=value.head, modifiers=value.modifiers)
        )

    if isinstance(value, NumberValue):
        return ProtoValue(number_value=value)

    if isinstance(value, NullValue):
        return ProtoValue(null_value=PROTO_NULL_VALUE)  # type: ignore

    if isinstance(value, TextValue):
        return ProtoValue(text_value=value)

    if isinstance(value, BooleanValue):
        return ProtoValue(boolean_value=value)

    if isinstance(value, OpaqueValue):
        return ProtoValue(
            opaque_value=ProtoOpaqueValue(
                content=value.value,
                is_a=[
                    ProtoNounPhrase(head=is_a.head, modifiers=is_a.modifiers)
                    for is_a in value.is_a
                ],
            )
        )

    if isinstance(value, bytes):
        return ProtoValue(opaque_value=ProtoOpaqueValue(content=value))

    if isinstance(value, DatetimeValue):
        seconds, nanos = _timestamp_to_seconds_and_nanos(value)
        return ProtoValue(
            datetime_value=google.protobuf.timestamp_pb2.Timestamp(  # pylint: disable=no-member
                seconds=seconds, nanos=nanos
            )
        )

    if isinstance(value, DateValue):
        return ProtoValue(
            date_value=ProtoDate(year=value.year, month=value.month, day=value.day)
        )

    if isinstance(value, TimeValue):
        return ProtoValue(
            time_value=ProtoTime(
                hours=value.hour,
                minutes=value.minute,
                seconds=value.second,
                nanos=_micros_to_nanos(value.microsecond),
            )
        )

    if isinstance(value, ListValue):
        return ProtoValue(
            list_value=ProtoListValue(values=[map_value(v) for v in value])
        )

    if isinstance(value, DictionaryValue):
        return ProtoValue(
            dictionary_value=ProtoDictionaryValue(
                fields=[
                    ProtoDictionaryValueField(key=k, value=map_value(v))
                    for k, v in value.value.items()
                ],
                is_a=[
                    ProtoNounPhrase(head=is_a.head, modifiers=is_a.modifiers)
                    for is_a in value.is_a
                ],
            )
        )

    if isinstance(value, dict):
        return ProtoValue(
            dictionary_value=ProtoDictionaryValue(
                fields=[
                    ProtoDictionaryValueField(key=k, value=map_value(v))
                    for k, v in value.items()
                ]
            )
        )

    if isinstance(value, RemoteFile):
        return ProtoValue(file_value=ProtoFileValue(remote=value.url))

    if isinstance(value, File):
        return ProtoValue(
            file_value=ProtoFileValue(
                inline=ProtoFile(file_name=value.filename, content=value.content)
            )
        )

    if isinstance(value, Table):
        return ProtoValue(
            table_value=ProtoTableValue(
                inline=ProtoTable(
                    columns=[
                        ProtoColumn(
                            name=c.name, values=[map_value(val) for val in c.values]
                        )
                        for c in value.columns
                    ]
                )
            )
        )

    if isinstance(value, RemoteTable):
        return ProtoValue(table_value=ProtoTableValue(remote=value.url))

    if isinstance(value, SensitiveValue):
        return ProtoValue(
            sensitive_value=ProtoSensitiveValue(value=map_value(value.value))
        )

    raise NotImplementedError(f"Can't map value '{value}' of type '{type(value)}'")
