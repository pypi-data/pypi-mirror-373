from typing import List

# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.responses.retrieve_discoverables_pb2 import \
    RetrieveDiscoverablesResponse as ProtoDiscoverablesResponse

from ..discoverable import Discoverable


def map_discoverables(
    data: ProtoDiscoverablesResponse,
) -> List[Discoverable]:
    return [
        Discoverable(name=d.name, description=d.description) for d in data.discoverables
    ]
