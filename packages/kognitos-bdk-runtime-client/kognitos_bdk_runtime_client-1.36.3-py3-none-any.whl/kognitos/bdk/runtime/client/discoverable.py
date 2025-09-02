from dataclasses import dataclass
from typing import Optional

from .base import BdkDescriptorBase


@dataclass
class Discoverable(BdkDescriptorBase):
    name: str
    description: Optional[str]
