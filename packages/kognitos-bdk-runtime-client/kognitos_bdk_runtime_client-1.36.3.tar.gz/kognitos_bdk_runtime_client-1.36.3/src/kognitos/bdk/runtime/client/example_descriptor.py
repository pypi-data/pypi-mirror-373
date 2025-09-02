from dataclasses import dataclass

from .base import BdkDescriptorBase


@dataclass
class ExampleDescriptor(BdkDescriptorBase):
    description: str
    snippet: str
