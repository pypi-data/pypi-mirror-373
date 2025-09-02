from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Offload(_message.Message):
    __slots__ = ('aws',)
    AWS_FIELD_NUMBER: _ClassVar[int]
    aws: AWSOffload

    def __init__(self, aws: _Optional[_Union[AWSOffload, _Mapping]]=...) -> None:
        ...

class AWSOffload(_message.Message):
    __slots__ = ('access_key', 'secret_key', 'session_token', 'region', 'bucket', 'folder_name', 'endpoint_url')
    ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
    SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    FOLDER_NAME_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_URL_FIELD_NUMBER: _ClassVar[int]
    access_key: str
    secret_key: str
    session_token: str
    region: str
    bucket: str
    folder_name: str
    endpoint_url: str

    def __init__(self, access_key: _Optional[str]=..., secret_key: _Optional[str]=..., session_token: _Optional[str]=..., region: _Optional[str]=..., bucket: _Optional[str]=..., folder_name: _Optional[str]=..., endpoint_url: _Optional[str]=...) -> None:
        ...