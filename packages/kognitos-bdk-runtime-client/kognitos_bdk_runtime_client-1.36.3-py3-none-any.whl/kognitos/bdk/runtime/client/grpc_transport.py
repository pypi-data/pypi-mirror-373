import functools
import json
from typing import Any, Callable, List, Optional, Tuple

import grpc

from . import mappers
from .book_descriptor import BookDescriptor
from .book_procedure_descriptor import BookProcedureDescriptor
from .discoverable import Discoverable
from .environment_information import EnvironmentInformation
from .exceptions import (AuthenticationRequired, BDKRuntimeClientError,
                         Internal, InvalidValue, NotFound, NotSupported,
                         handle_exception)
from .expression import Expression
from .input_mappers import (map_answered_questions, map_authentication,
                            map_expression, map_input_concepts, map_offload,
                            map_promise)
from .input_mappers.input_concepts import InputConcept
from .offload import Offload
from .promise import Promise
from .proto.requests.discover_procedures_pb2 import \
    DiscoverProceduresRequest  # pylint: disable=no-name-in-module
from .proto.requests.environment_information_pb2 import \
    EnvironmentInformationRequest  # pylint: disable=no-name-in-module
from .proto.requests.invoke_procedure_pb2 import \
    InvokeProcedureRequest  # pylint: disable=no-name-in-module
from .proto.requests.resolve_promise_pb2 import \
    ResolvePromiseRequest  # pylint: disable=no-name-in-module
from .proto.requests.retrieve_book_pb2 import \
    RetrieveBookRequest  # pylint: disable=no-name-in-module
from .proto.requests.retrieve_book_procedures_pb2 import \
    RetrieveBookProceduresRequest  # pylint: disable=no-name-in-module
from .proto.requests.retrieve_books_pb2 import \
    RetrieveBooksRequest  # pylint: disable=no-name-in-module
from .proto.requests.retrieve_discoverables_pb2 import \
    RetrieveDiscoverablesRequest  # pylint: disable=no-name-in-module
from .proto.requests.retrieve_tags_pb2 import \
    RetrieveTagsRequest  # pylint: disable=no-name-in-module
from .proto.requests.test_connection_pb2 import \
    TestConnectionRequest  # pylint: disable=no-name-in-module
from .proto.responses.error_pb2 import \
    Error  # pylint: disable=no-name-in-module
from .proto.services.book_pb2_grpc import \
    BookServiceStub  # pylint: disable=no-name-in-module
from .proto.services.library_pb2_grpc import \
    LibraryServiceStub  # pylint: disable=no-name-in-module
from .question_answer import AnsweredQuestion
from .request_context import RequestContext
from .transport import InvokeProcedureResponse, Transport


def _get_metadata(
    context: Optional[RequestContext] = None,
) -> List[Tuple[str, str]]:
    """
    Creates gRPC metadata as a list of (key, value) tuples.
    Context fields are passed as individual headers, binary values are base64 encoded.
    """
    metadata = []

    # Add context fields as individual headers
    if context:
        if context.trace_id is not None:
            metadata.append(("trace-id", str(context.trace_id)))
        if context.span_id is not None:
            metadata.append(("span-id", str(context.span_id)))
        if context.worker_id is not None:
            metadata.append(("x-bdk-worker-id", context.worker_id))
        if context.department_id is not None:
            metadata.append(("x-bdk-department-id", context.department_id))
        if context.knowledge_id is not None:
            metadata.append(("x-bdk-knowledge-id", context.knowledge_id))
        if context.line_id is not None:
            metadata.append(("x-bdk-line-id", context.line_id))

    return metadata


bdk_error_mapping = {
    grpc.StatusCode.OK: "ok",
    grpc.StatusCode.CANCELLED: "cancelled",
    grpc.StatusCode.UNKNOWN: "unknown",
    grpc.StatusCode.INVALID_ARGUMENT: InvalidValue,
    grpc.StatusCode.DEADLINE_EXCEEDED: "deadline_exceeded",
    grpc.StatusCode.NOT_FOUND: NotFound,
    grpc.StatusCode.ALREADY_EXISTS: "already_exists",
    grpc.StatusCode.PERMISSION_DENIED: "permission_denied",
    grpc.StatusCode.RESOURCE_EXHAUSTED: "resource_exhausted",
    grpc.StatusCode.FAILED_PRECONDITION: "failed_precondition",
    grpc.StatusCode.ABORTED: "aborted",
    grpc.StatusCode.OUT_OF_RANGE: "out_of_range",
    grpc.StatusCode.UNIMPLEMENTED: NotSupported,
    grpc.StatusCode.INTERNAL: Internal,
    grpc.StatusCode.UNAVAILABLE: "unavailable",
    grpc.StatusCode.DATA_LOSS: "data_loss",
    grpc.StatusCode.UNAUTHENTICATED: AuthenticationRequired,
}


def handle_grpc_exception(exc: grpc.RpcError) -> None:
    """
    Handle gRPC exceptions by mapping them to appropriate BDK exceptions.
    This function always raises an exception and never returns normally.
    """
    # There's the grpc._InactiveRpcError that is the one thrown.
    # That inherits from grpc.RpcError and grpc.Call, which is the one that provides the error information
    if isinstance(exc, grpc.Call) and exc.code():
        if exc.code() == grpc.StatusCode.INTERNAL:
            error = _build_proto_error_from_metadata(exc)
            handle_exception(error)

        # Standard gRPC status code mapping
        if exc.code() in bdk_error_mapping:
            mapping = bdk_error_mapping[exc.code()]
            if not isinstance(mapping, str):
                raise mapping(exc.details()) from exc
        raise BDKRuntimeClientError(
            f"gRPC error [{exc.code()}]: {exc.details()}"
        ) from exc

    raise BDKRuntimeClientError(f"Unexpected gRPC error: {exc}") from exc


def _build_proto_error_from_metadata(exc):
    metadata = dict(exc.trailing_metadata()) if exc.trailing_metadata() else {}
    # Extract error information from metadata
    kind_str = metadata.get("error_kind", "0")
    kind = int(kind_str) if kind_str.isdigit() else 0
    message = metadata.get("error_message", exc.details())
    extra = None
    extra_str = metadata.get("error_extra")
    if extra_str:
        try:
            extra = json.loads(extra_str)
        except (json.JSONDecodeError, TypeError):
            extra = None
    # Create Error object and handle it using the standard error handling
    error = Error(kind=kind, message=message, extra=extra)  # type: ignore
    return error


# pylint: disable=inconsistent-return-statements
def grpc_request(func: Callable) -> Callable:
    """Decorator to handle gRPC exceptions."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except grpc.RpcError as e:
            handle_grpc_exception(e)

    return wrapper


class GRPCTransport(Transport):
    def __init__(self, url: str):
        self.url = url
        channel = grpc.insecure_channel(url)
        self.stub = BookServiceStub(channel)
        self.library_stub = LibraryServiceStub(channel)

    def get_url(self) -> str:
        return self.url

    @grpc_request
    def retrieve_books(
        self, context: Optional[RequestContext] = None
    ) -> List[BookDescriptor]:
        res = self.stub.RetrieveBooks(
            RetrieveBooksRequest(), metadata=_get_metadata(context)
        )
        return [mappers.map_book_descriptor(b) for b in res.books]

    @grpc_request
    def environment_information(
        self, context: Optional[RequestContext] = None
    ) -> EnvironmentInformation:
        res = self.stub.EnvironmentInformation(
            EnvironmentInformationRequest(), metadata=_get_metadata(context)
        )
        return mappers.map_environment_information(res)

    @grpc_request
    def retrieve_book(
        self, name: str, version: str, context: Optional[RequestContext] = None
    ) -> BookDescriptor:
        res = self.stub.RetrieveBook(
            RetrieveBookRequest(name=name, version=version),
            metadata=_get_metadata(context),
        )
        return mappers.map_book_descriptor(res.book)

    @grpc_request
    def retrieve_procedures(
        self,
        name: str,
        version: str,
        include_connect: bool,
        context: Optional[RequestContext] = None,
    ) -> List[BookProcedureDescriptor]:
        res = self.stub.RetrieveBookProcedures(
            RetrieveBookProceduresRequest(
                name=name, version=version, include_connect=include_connect
            ),
            metadata=_get_metadata(context),
        )
        return [mappers.map_book_procedure_descriptor_v2(p) for p in res.procedures]

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    @grpc_request
    def test_connection(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        context: Optional[RequestContext] = None,
    ) -> Any:
        res = self.stub.TestConnection(
            TestConnectionRequest(
                name=name,
                version=version,
                authentication=map_authentication(
                    authentication_id, authentication_credentials
                ),
            ),
            metadata=_get_metadata(context),
        )
        return mappers.map_test_connection_response(res)

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    @grpc_request
    def invoke_procedure(
        self,
        name: str,
        version: str,
        procedure_id: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        input_concepts: List[InputConcept],
        context: Optional[RequestContext] = None,
        filter_expression: Optional[Expression] = None,
        offload: Optional[Offload] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        answered_questions: Optional[List[AnsweredQuestion]] = None,
    ) -> InvokeProcedureResponse:
        if answered_questions is None:
            answered_questions = []

        res = self.stub.InvokeProcedure(
            InvokeProcedureRequest(
                name=name,
                version=version,
                procedure_id=procedure_id,
                authentication=map_authentication(
                    authentication_id, authentication_credentials
                ),
                input_concepts=map_input_concepts(input_concepts),
                filter_expression=map_expression(filter_expression),
                offload=map_offload(offload),
                offset=offset,
                limit=limit,
                answered_questions=map_answered_questions(answered_questions),
            ),
            metadata=_get_metadata(context),
        )
        match res.WhichOneof("response_discriminator"):
            case "response":
                return mappers.map_concept_values(res.response.output_concepts)
            case "question":
                return mappers.map_questions(res.question.questions)
            case "promise":
                return mappers.map_promise(res.promise.promise)
            case _:
                raise NotImplementedError(
                    f"Unknown response type: {res.WhichOneof('response_discriminator')}"
                )

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    @grpc_request
    def discover_procedures(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        what: List[str],
        context: Optional[RequestContext] = None,
    ) -> List[BookProcedureDescriptor]:
        res = self.stub.DiscoverProcedures(
            DiscoverProceduresRequest(
                name=name,
                version=version,
                authentication=map_authentication(
                    authentication_id, authentication_credentials
                ),
                what=what,
            ),
            metadata=_get_metadata(context),
        )
        return [mappers.map_book_procedure_descriptor_v2(p) for p in res.procedures]

    @grpc_request
    def retrieve_discoverables(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        search: Optional[str],
        limit: Optional[int],
        offset: Optional[int],
        context: Optional[RequestContext] = None,
    ) -> List[Discoverable]:
        res = self.stub.RetrieveDiscoverables(
            RetrieveDiscoverablesRequest(
                name=name,
                version=version,
                authentication=map_authentication(
                    authentication_id, authentication_credentials
                ),
                search=search,
                limit=limit,
                offset=offset,
            ),
            metadata=_get_metadata(context),
        )
        return mappers.map_discoverables(res)

    @grpc_request
    def retrieve_tags(self, context: Optional[RequestContext] = None) -> List[str]:
        res = self.library_stub.RetrieveTags(
            RetrieveTagsRequest(), metadata=_get_metadata(context)
        )
        return res.tags

    @grpc_request
    def resolve_promise(
        self,
        name: str,
        version: str,
        procedure_id: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        promise: Promise,
        configurations: List[InputConcept],
        offload: Optional[Offload] = None,
        answered_questions: Optional[List[AnsweredQuestion]] = None,
        context: Optional[RequestContext] = None,
    ) -> InvokeProcedureResponse:
        if answered_questions is None:
            answered_questions = []

        res = self.stub.ResolvePromise(
            ResolvePromiseRequest(
                name=name,
                version=version,
                authentication=map_authentication(
                    authentication_id, authentication_credentials
                ),
                procedure_id=procedure_id,
                promise=map_promise(promise),
                offload=map_offload(offload),
                answered_questions=map_answered_questions(answered_questions),
                configurations=map_input_concepts(configurations),
            ),
            metadata=_get_metadata(context),
        )
        match res.WhichOneof("response_discriminator"):
            case "response":
                return mappers.map_concept_values(res.response.output_concepts)
            case "question":
                return mappers.map_questions(res.question.questions)
            case "promise":
                return mappers.map_promise(res.promise.promise)
            case _:
                raise NotImplementedError(
                    f"Unknown response type: {res.WhichOneof('response_discriminator')}"
                )
