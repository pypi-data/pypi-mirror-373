from dataclasses import dataclass
from typing import List

from .base import BdkDescriptorBase


@dataclass
class EnvironmentInformation(BdkDescriptorBase):
    version: str
    runtime_name: str
    runtime_version: str
    bci_protocol_version: str
    api_version: str
    path: List[str]
