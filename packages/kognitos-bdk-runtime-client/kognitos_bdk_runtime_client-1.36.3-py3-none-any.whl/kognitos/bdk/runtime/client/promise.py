from dataclasses import dataclass

from .base import BdkDescriptorBase
from .value import Value


@dataclass
class Promise(BdkDescriptorBase):
    promise_resolver_function_name: str
    data: Value
