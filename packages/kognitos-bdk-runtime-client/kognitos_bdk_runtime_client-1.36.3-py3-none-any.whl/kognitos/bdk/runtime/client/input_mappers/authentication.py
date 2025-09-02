from typing import List, Optional, Tuple, Union

from kognitos.bdk.runtime.client.sensitive import Sensitive

from ..proto.requests.authentication_pb2 import (  # pylint: disable=no-name-in-module
    Authentication, CredentialValue)
from .value import map_value


def map_authentication(
    authentication_id: Optional[str],
    authentication_credentials: Optional[List[Tuple[str, Union[str, Sensitive]]]],
) -> Optional[Authentication]:
    parsed_credentials = (
        [
            CredentialValue(id=c[0], value=map_value(c[1]))
            for c in authentication_credentials
        ]
        if authentication_credentials
        else None
    )

    authentication = (
        Authentication(
            authentication_id=authentication_id,
            authentication_credentials=parsed_credentials,
        )
        if authentication_id
        else None
    )

    return authentication
