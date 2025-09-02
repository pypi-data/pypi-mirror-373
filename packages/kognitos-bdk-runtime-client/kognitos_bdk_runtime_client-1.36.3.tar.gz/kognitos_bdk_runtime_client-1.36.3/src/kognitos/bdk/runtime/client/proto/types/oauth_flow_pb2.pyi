from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar
DESCRIPTOR: _descriptor.FileDescriptor

class OAuthFlow(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OAuthFlowAuthorizationCode: _ClassVar[OAuthFlow]
    OAuthFlowClientCredentials: _ClassVar[OAuthFlow]
OAuthFlowAuthorizationCode: OAuthFlow
OAuthFlowClientCredentials: OAuthFlow