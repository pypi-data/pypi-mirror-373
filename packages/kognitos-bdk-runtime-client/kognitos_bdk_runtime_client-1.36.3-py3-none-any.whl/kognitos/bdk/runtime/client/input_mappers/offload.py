from typing import Optional

from kognitos.bdk.runtime.client.offload import AWSOffload, Offload
from kognitos.bdk.runtime.client.proto.requests.offload_pb2 import \
    AWSOffload as ProtoAWSOffload  # pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.requests.offload_pb2 import \
    Offload as ProtoOffload  # pylint: disable=no-name-in-module


def map_offload(offload: Optional[Offload]) -> Optional[ProtoOffload]:
    if not offload:
        return None

    if isinstance(offload, AWSOffload):
        return ProtoOffload(
            aws=ProtoAWSOffload(
                access_key=offload.access_key,
                secret_key=offload.secret_key,
                session_token=offload.session_token,
                region=offload.region,
                bucket=offload.bucket,
                folder_name=offload.folder_name,
            )
        )

    raise ValueError(f"Unknown offload type: {offload}")
