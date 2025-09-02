from dataclasses import dataclass
from enum import Enum

from .base import BdkDescriptorBase


class CredentialType(Enum):
    CREDENTIAL_TYPE_TEXT = 0
    CREDENTIAL_TYPE_SENSITIVE_TEXT = 1


@dataclass
class CredentialDescriptor(BdkDescriptorBase):
    id: str
    type: CredentialType
    label: str
    visible: bool
    description: str
