from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar
DESCRIPTOR: _descriptor.FileDescriptor

class OAuthProvider(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OAuthProviderMicrosoft: _ClassVar[OAuthProvider]
    OAuthProviderGoogle: _ClassVar[OAuthProvider]
    OAuthProviderGeneric: _ClassVar[OAuthProvider]
OAuthProviderMicrosoft: OAuthProvider
OAuthProviderGoogle: OAuthProvider
OAuthProviderGeneric: OAuthProvider