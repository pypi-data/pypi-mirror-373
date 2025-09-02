from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional
DESCRIPTOR: _descriptor.FileDescriptor

class Context(_message.Message):
    __slots__ = ('trace_id', 'span_id', 'worker_id', 'department_id', 'knowledge_id', 'line_id')
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    KNOWLEDGE_ID_FIELD_NUMBER: _ClassVar[int]
    LINE_ID_FIELD_NUMBER: _ClassVar[int]
    trace_id: int
    span_id: int
    worker_id: str
    department_id: str
    knowledge_id: str
    line_id: str

    def __init__(self, trace_id: _Optional[int]=..., span_id: _Optional[int]=..., worker_id: _Optional[str]=..., department_id: _Optional[str]=..., knowledge_id: _Optional[str]=..., line_id: _Optional[str]=...) -> None:
        ...