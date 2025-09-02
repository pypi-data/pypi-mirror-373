from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar
DESCRIPTOR: _descriptor.FileDescriptor

class ConnectionRequired(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Optional: _ClassVar[ConnectionRequired]
    Always: _ClassVar[ConnectionRequired]
    Never: _ClassVar[ConnectionRequired]
Optional: ConnectionRequired
Always: ConnectionRequired
Never: ConnectionRequired