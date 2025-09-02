# pylint: disable=no-name-in-module
from typing import Dict, Optional

from .proto.responses.error_pb2 import Error


class BDKRuntimeClientError(RuntimeError):
    def __init__(self, message: str, extra: Optional[Dict] = None):
        self.message = message
        self.extra = extra
        super().__init__(message)


class TransportBuildError(RuntimeError):
    pass


#
# Mappings from Proto
#
class Internal(BDKRuntimeClientError):
    pass


class NotFound(BDKRuntimeClientError):
    pass


class NotSupported(BDKRuntimeClientError):
    pass


class MissingValue(BDKRuntimeClientError):
    pass


class InvalidValue(BDKRuntimeClientError):
    pass


class HTTPError(BDKRuntimeClientError):
    pass


class RateLimit(BDKRuntimeClientError):
    pass


class AccessDenied(BDKRuntimeClientError):
    pass


class TypeMismatch(BDKRuntimeClientError):
    pass


class TLSError(BDKRuntimeClientError):
    pass


class AuthenticationRequired(BDKRuntimeClientError):
    pass


error_kind_mappings = {
    0: Internal,
    1: NotFound,
    2: NotSupported,
    3: MissingValue,
    4: InvalidValue,
    5: HTTPError,
    6: RateLimit,
    7: AccessDenied,
    8: TypeMismatch,
    9: TLSError,
    10: AuthenticationRequired,
}


#
# Runtime Client Specific
#


class UnexpectedResponse(RuntimeError):
    pass


class UnexpectedException(RuntimeError):
    pass


class UnsupportedProtocolVersion(RuntimeError):
    pass


def handle_exception(error: Error):
    error_kind = error.kind
    error_message = error.message
    extra = error.extra

    try:
        raise error_kind_mappings[error_kind](error_message, extra)
    except KeyError as exc:
        raise UnexpectedException(
            f"There's no definition of error kind '{error_kind}' in the bdk-runtime-client, please reach out to integrations team."
        ) from exc
