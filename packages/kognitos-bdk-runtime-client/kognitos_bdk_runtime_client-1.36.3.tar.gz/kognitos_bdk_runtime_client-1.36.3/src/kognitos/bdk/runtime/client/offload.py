from dataclasses import dataclass
from typing import Union


@dataclass
class AWSOffload:
    access_key: str
    secret_key: str
    session_token: str
    region: str
    bucket: str
    folder_name: str


Offload = Union[AWSOffload,]  # pyright: ignore [reportInvalidTypeArguments]
