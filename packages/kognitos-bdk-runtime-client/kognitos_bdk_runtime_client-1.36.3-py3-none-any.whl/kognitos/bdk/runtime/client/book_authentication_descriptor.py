from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

from kognitos.bdk.runtime.client.noun_phrase import NounPhrase

from .base import BdkDescriptorBase
from .credential_descriptor import CredentialDescriptor


@dataclass
class BookCustomAuthenticationDescriptor(BdkDescriptorBase):
    id: str
    credentials: List[CredentialDescriptor]
    description: str
    name: str
    noun_phrase: Optional[NounPhrase]


class OauthProvider(Enum):
    OAUTH_PROVIDER_MICROSOFT = 0
    OAUTH_PROVIDER_GOOGLE = 1
    OAUTH_PROVIDER_GENERIC = 2


class OauthFlow(Enum):
    OAUTH_FLOW_AUTHORIZATION_CODE = 0
    OAUTH_FLOW_CLIENT_CREDENTIALS = 1


@dataclass
class OauthArgumentDescriptor(BdkDescriptorBase):
    id: str
    name: str
    description: str


@dataclass
class BookOAuthAuthenticationDescriptor(BdkDescriptorBase):
    id: str
    provider: OauthProvider
    flows: List[OauthFlow]
    authorize_endpoint: str
    token_endpoint: str
    scope: List[str]
    name: str
    arguments: List[OauthArgumentDescriptor]


BookAuthenticationDescriptor = Union[
    BookCustomAuthenticationDescriptor, BookOAuthAuthenticationDescriptor
]
