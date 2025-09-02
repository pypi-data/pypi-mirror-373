from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional
DESCRIPTOR: _descriptor.FileDescriptor

class TokenPaginationRequest(_message.Message):
    __slots__ = ('start_token', 'count')
    START_TOKEN_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    start_token: str
    count: str

    def __init__(self, start_token: _Optional[str]=..., count: _Optional[str]=...) -> None:
        ...

class TokenPaginationResponse(_message.Message):
    __slots__ = ('next_token',)
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    next_token: str

    def __init__(self, next_token: _Optional[str]=...) -> None:
        ...

class PagePaginationRequest(_message.Message):
    __slots__ = ('page', 'page_size')
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int

    def __init__(self, page: _Optional[int]=..., page_size: _Optional[int]=...) -> None:
        ...

class PagePaginationResponse(_message.Message):
    __slots__ = ('has_more', 'total_count', 'current_page')
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    has_more: bool
    total_count: int
    current_page: int

    def __init__(self, has_more: bool=..., total_count: _Optional[int]=..., current_page: _Optional[int]=...) -> None:
        ...