from types import book_custom_authentication_descriptor_pb2 as _book_custom_authentication_descriptor_pb2
from types import book_oauh_authentication_descriptor_pb2 as _book_oauh_authentication_descriptor_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class BookAuthenticationDescriptor(_message.Message):
    __slots__ = ('custom', 'oauth')
    CUSTOM_FIELD_NUMBER: _ClassVar[int]
    OAUTH_FIELD_NUMBER: _ClassVar[int]
    custom: _book_custom_authentication_descriptor_pb2.BookCustomAuthenticationDescriptor
    oauth: _book_oauh_authentication_descriptor_pb2.BookOAuthAuthenticationDescriptor

    def __init__(self, custom: _Optional[_Union[_book_custom_authentication_descriptor_pb2.BookCustomAuthenticationDescriptor, _Mapping]]=..., oauth: _Optional[_Union[_book_oauh_authentication_descriptor_pb2.BookOAuthAuthenticationDescriptor, _Mapping]]=...) -> None:
        ...