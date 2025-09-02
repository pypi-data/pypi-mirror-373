from abc import abstractmethod
from typing import Any, List, Literal, Optional, Tuple

from . import input_mappers, mappers
from .book_descriptor import BookDescriptor
from .book_procedure_descriptor import BookProcedureDescriptor
from .discoverable import Discoverable
from .environment_information import EnvironmentInformation
from .exceptions import UnexpectedResponse, handle_exception
from .expression import Expression
from .input_mappers.input_concepts import InputConcept
from .offload import Offload
from .promise import Promise
from .proto.requests.context_pb2 import \
    Context  # pylint: disable=no-name-in-module
from .proto.requests.discover_procedures_pb2 import \
    DiscoverProceduresRequest  # pylint: disable=no-name-in-module
from .proto.requests.environment_information_pb2 import \
    EnvironmentInformationRequest  # pylint: disable=no-name-in-module
from .proto.requests.invoke_procedure_pb2 import \
    InvokeProcedureRequest  # pylint: disable=no-name-in-module
from .proto.requests.request_pb2 import \
    Request  # pylint: disable=no-name-in-module
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
from .proto.responses.response_pb2 import \
    Response  # pylint: disable=no-name-in-module
from .question_answer import AnsweredQuestion
from .request_context import RequestContext
from .transport import InvokeProcedureResponse, Transport


def map_context(context: Optional[RequestContext]) -> Context:
    if not context:
        context = RequestContext()

    return Context(
        trace_id=context.trace_id,
        span_id=context.span_id,
        worker_id=context.worker_id,
        department_id=context.department_id,
        knowledge_id=context.knowledge_id,
        line_id=context.line_id,
    )


ResponseFieldLiteral = Literal[
    "environment_information",
    "error",
    "invoked_procedure",
    "retrieved_book",
    "retrieved_books",
    "retrieved_procedures",
    "tested_connection",
    "discovered_procedures",
    "promise",
    "question",
    "retrieved_discoverables",
    "retrieved_tags",
]


def handle_response(
    response: Response,
    response_field: ResponseFieldLiteral | List[ResponseFieldLiteral],
):
    if not isinstance(response_field, list):
        response_field = [response_field]

    if response.HasField("error"):
        handle_exception(response.error)
    if not any(response.HasField(field) for field in response_field):
        raise UnexpectedResponse(
            f"Didn't get any of the expected responses {response_field} from server"
        )
    response_field = next(field for field in response_field if response.HasField(field))
    return getattr(response, response_field)


class BaseTransport(Transport):
    @abstractmethod
    def send(self, request: Request) -> Response:
        pass

    def retrieve_books(
        self, context: Optional[RequestContext] = None
    ) -> List[BookDescriptor]:
        request = Request(
            retrieve_books=RetrieveBooksRequest(), context=map_context(context)
        )
        response = handle_response(self.send(request), "retrieved_books")
        return [mappers.map_book_descriptor(b) for b in response.books]

    def environment_information(
        self, context: Optional[RequestContext] = None
    ) -> EnvironmentInformation:
        request = Request(
            environment_information=EnvironmentInformationRequest(),
            context=map_context(context),
        )
        return mappers.map_environment_information(
            handle_response(self.send(request), "environment_information")
        )

    def retrieve_book(
        self, name, version, context: Optional[RequestContext] = None
    ) -> BookDescriptor:
        request = Request(
            retrieve_book=RetrieveBookRequest(name=name, version=version),
            context=map_context(context),
        )
        response = handle_response(self.send(request), "retrieved_book")
        return mappers.map_book_descriptor(response.book)

    def retrieve_procedures(
        self,
        name: str,
        version: str,
        include_connect: bool,
        context: Optional[RequestContext] = None,
    ) -> List[BookProcedureDescriptor]:
        request = Request(
            retrieve_procedures=RetrieveBookProceduresRequest(
                name=name, version=version, include_connect=include_connect
            ),
            context=map_context(context),
        )

        response = handle_response(self.send(request), "retrieved_procedures")

        return [mappers.map_book_procedure_descriptor(ps) for ps in response.procedures]

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def test_connection(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        context: Optional[RequestContext] = None,
    ) -> Any:
        authentication = input_mappers.map_authentication(
            authentication_id, authentication_credentials
        )

        request = Request(
            test_connection=TestConnectionRequest(
                name=name, version=version, authentication=authentication
            ),
            context=map_context(context),
        )

        response = handle_response(self.send(request), "tested_connection")

        return mappers.map_test_connection_response(response)

    # pylint: disable=too-many-arguments, too-many-locals
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

        request = Request(
            invoke_procedure=InvokeProcedureRequest(
                name=name,
                version=version,
                procedure_id=procedure_id,
                authentication=input_mappers.map_authentication(
                    authentication_id, authentication_credentials
                ),
                input_concepts=input_mappers.map_input_concepts(input_concepts),
                filter_expression=input_mappers.map_expression(filter_expression),
                offload=input_mappers.map_offload(offload),
                offset=offset,
                limit=limit,
                answered_questions=input_mappers.map_answered_questions(
                    answered_questions
                ),
            ),
            context=map_context(context),
        )

        response = handle_response(
            self.send(request), ["invoked_procedure", "question", "promise"]
        )

        if hasattr(
            response, "questions"
        ):  # HasField raises ValueError instead of yielding False
            return mappers.map_questions(response.questions)

        if hasattr(
            response, "promise"
        ):  # HasField raises ValueError instead of yielding False
            return mappers.map_promise(response.promise)

        return mappers.map_concept_values(response.output_concepts)

    def discover_procedures(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        what: List[str],
        context: Optional[RequestContext] = None,
    ) -> List[BookProcedureDescriptor]:

        request = Request(
            discover_procedures=DiscoverProceduresRequest(
                name=name,
                version=version,
                authentication=input_mappers.map_authentication(
                    authentication_id, authentication_credentials
                ),
                what=what,
            ),
            context=map_context(context),
        )

        response = handle_response(self.send(request), "discovered_procedures")

        return [mappers.map_book_procedure_descriptor(p) for p in response.procedures]

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

        request = Request(
            retrieve_discoverables=RetrieveDiscoverablesRequest(
                name=name,
                version=version,
                authentication=input_mappers.map_authentication(
                    authentication_id, authentication_credentials
                ),
                search=search,
                limit=limit,
                offset=offset,
            ),
            context=map_context(context),
        )

        response = handle_response(self.send(request), "retrieved_discoverables")

        return mappers.map_discoverables(response)

    def retrieve_tags(self, context: Optional[RequestContext] = None) -> List[str]:
        request = Request(
            retrieve_tags=RetrieveTagsRequest(),
            context=map_context(context),
        )
        response = handle_response(self.send(request), "retrieved_tags")
        return response.tags

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

        request = Request(
            resolve_promise=ResolvePromiseRequest(
                name=name,
                version=version,
                authentication=input_mappers.map_authentication(
                    authentication_id, authentication_credentials
                ),
                procedure_id=procedure_id,
                promise=input_mappers.map_promise(promise),
                offload=input_mappers.map_offload(offload),
                answered_questions=input_mappers.map_answered_questions(
                    answered_questions
                ),
                configurations=input_mappers.map_input_concepts(configurations),
            ),
            context=map_context(context),
        )

        response = handle_response(
            self.send(request), ["invoked_procedure", "question", "promise"]
        )

        if hasattr(
            response, "questions"
        ):  # HasField raises ValueError instead of yielding False
            return mappers.map_questions(response.questions)

        if hasattr(
            response, "promise"
        ):  # HasField raises ValueError instead of yielding False
            return mappers.map_promise(response.promise)

        return mappers.map_concept_values(response.output_concepts)
