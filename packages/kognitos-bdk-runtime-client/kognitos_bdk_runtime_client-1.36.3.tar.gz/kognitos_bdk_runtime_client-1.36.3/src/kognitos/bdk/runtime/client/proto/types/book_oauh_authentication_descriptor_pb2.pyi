from types import oauth_argument_descriptor_pb2 as _oauth_argument_descriptor_pb2
from types import oauth_flow_pb2 as _oauth_flow_pb2
from types import oauth_provider_pb2 as _oauth_provider_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class BookOAuthAuthenticationDescriptor(_message.Message):
    __slots__ = ('id', 'provider', 'flows', 'authorize_endpoint', 'token_endpoint', 'scope', 'name', 'arguments')
    ID_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    FLOWS_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZE_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    TOKEN_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    provider: _oauth_provider_pb2.OAuthProvider
    flows: _containers.RepeatedScalarFieldContainer[_oauth_flow_pb2.OAuthFlow]
    authorize_endpoint: str
    token_endpoint: str
    scope: _containers.RepeatedScalarFieldContainer[str]
    name: str
    arguments: _containers.RepeatedCompositeFieldContainer[_oauth_argument_descriptor_pb2.OAuthArgumentDescriptor]

    def __init__(self, id: _Optional[str]=..., provider: _Optional[_Union[_oauth_provider_pb2.OAuthProvider, str]]=..., flows: _Optional[_Iterable[_Union[_oauth_flow_pb2.OAuthFlow, str]]]=..., authorize_endpoint: _Optional[str]=..., token_endpoint: _Optional[str]=..., scope: _Optional[_Iterable[str]]=..., name: _Optional[str]=..., arguments: _Optional[_Iterable[_Union[_oauth_argument_descriptor_pb2.OAuthArgumentDescriptor, _Mapping]]]=...) -> None:
        ...