import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from kognitos.bdk.runtime.client.noun_phrase import \
    NounPhrase  # pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.sensitive import \
    Sensitive  # pylint: disable=no-name-in-module

from .base import BdkDescriptorBase

NoneType = type(None)


@dataclass
class RemoteFile(BdkDescriptorBase):
    url: str

    def human_readable(self) -> str:
        """
        Returns a string representation of the RemoteFile.
        """
        return "RemoteFile"


@dataclass
class File(BdkDescriptorBase):
    filename: str
    content: bytes

    def human_readable(self) -> str:
        """
        Returns a string representation of the File.
        """
        return "File"


FileValue = Union[RemoteFile, File]


@dataclass
class DictionaryValue(BdkDescriptorBase):
    value: Dict[str, "Value"]
    is_a: List[NounPhrase] = field(default_factory=list)

    def human_readable(self) -> str:
        """
        Returns a string representation of the DictionaryValue.
        """
        str_is_a = [str(is_a) for is_a in self.is_a]
        return f"Object({', '.join(str_is_a)})"

    def as_dict(self) -> Dict[str, Any]:
        """
        Returns the DictionaryValue as a native Python dictionary.
        """

        def _convert_value(value: "Value") -> Any:

            if isinstance(value, DictionaryValue):
                return value.as_dict()
            if isinstance(value, list):
                return [_convert_value(v) for v in value]

            return value

        return {k: _convert_value(v) for k, v in self.value.items()}


@dataclass
class OpaqueValue(BdkDescriptorBase):
    value: bytes
    is_a: List[NounPhrase] = field(default_factory=list)

    def human_readable(self) -> str:
        """
        Returns a string representation of the OpaqueValue.
        """
        # turn into comma separated string
        str_is_a = [str(is_a) for is_a in self.is_a]
        return f"Object({', '.join(str_is_a)})"


@dataclass
class RemoteTable(BdkDescriptorBase):
    url: str

    def human_readable(self) -> str:
        """
        Returns a string representation of the RemoteTable.
        """
        return "RemoteTable"


@dataclass
class Column:
    name: str
    values: List["Value"]

    def human_readable(self) -> str:
        """
        Returns a string representation of the Column.
        """
        return f"Column(name={self.name})"


@dataclass
class Table(BdkDescriptorBase):
    columns: List[Column]

    def human_readable(self) -> str:
        """
        Returns a string representation of a Table.
        """
        column_names = [column.name for column in self.columns]
        column_names_str = ", ".join(column_names)
        return f"Table with columns: {column_names_str}"


TableValue = Union[Table, RemoteTable]


NullValue = type(None)
TextValue = str
NumberValue = float
BooleanValue = bool
ConceptualValue = NounPhrase
DatetimeValue = datetime.datetime
DateValue = datetime.date
TimeValue = datetime.time
ListValue = List
SensitiveValue = Sensitive

Value = Union[
    ConceptualValue,
    NumberValue,
    NullValue,
    TextValue,
    BooleanValue,
    FileValue,
    OpaqueValue,
    DictionaryValue,
    ListValue,
    DatetimeValue,
    DateValue,
    TimeValue,
    TableValue,
    SensitiveValue,
]
