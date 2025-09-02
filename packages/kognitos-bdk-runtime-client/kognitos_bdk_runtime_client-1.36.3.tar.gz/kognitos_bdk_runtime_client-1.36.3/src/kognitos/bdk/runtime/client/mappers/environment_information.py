# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.responses.environment_information_pb2 import \
    EnvironmentInformationResponse as ProtoEnvironmentInformation

from ..environment_information import EnvironmentInformation


def map_environment_information(
    data: ProtoEnvironmentInformation,
) -> EnvironmentInformation:
    return EnvironmentInformation(
        version=data.version,
        runtime_name=data.runtime_name,
        runtime_version=data.runtime_version,
        bci_protocol_version=data.bci_protocol_version,
        api_version=data.api_version,
        path=list(data.path),
    )
