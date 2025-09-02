from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from .book_descriptor import BookDescriptor
from .book_procedure_descriptor import BookProcedureDescriptor
from .concept_value import ConceptValue
from .discoverable import Discoverable
from .environment_information import EnvironmentInformation
from .expression import Expression
from .input_mappers.input_concepts import InputConcept
from .offload import Offload
from .promise import Promise
from .question_answer import AnsweredQuestion, Question
from .request_context import RequestContext

InvokeProcedureResponse = List[ConceptValue] | List[Question] | Promise


class TransportError(Exception):
    pass


class Transport(ABC):
    @abstractmethod
    def get_url(self) -> str:
        pass

    @abstractmethod
    def retrieve_books(
        self, context: Optional[RequestContext] = None
    ) -> List[BookDescriptor]:
        pass

    @abstractmethod
    def environment_information(
        self, context: Optional[RequestContext] = None
    ) -> EnvironmentInformation:
        pass

    @abstractmethod
    def retrieve_book(
        self, name: str, version: str, context: Optional[RequestContext] = None
    ) -> BookDescriptor:
        pass

    @abstractmethod
    def retrieve_procedures(
        self,
        name: str,
        version: str,
        include_connect: bool,
        context: Optional[RequestContext] = None,
    ) -> List[BookProcedureDescriptor]:
        pass

    @abstractmethod
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def test_connection(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        context: Optional[RequestContext] = None,
    ) -> Any:
        pass

    @abstractmethod
    # pylint: disable=too-many-arguments, too-many-positional-arguments
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
        pass

    @abstractmethod
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def discover_procedures(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        what: List[str],
        context: Optional[RequestContext] = None,
    ) -> List[BookProcedureDescriptor]:
        pass

    @abstractmethod
    # pylint: disable=too-many-arguments, too-many-positional-arguments
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
        pass

    @abstractmethod
    def retrieve_tags(self, context: Optional[RequestContext] = None) -> List[str]:
        pass

    @abstractmethod
    # pylint: disable=too-many-arguments, too-many-positional-arguments
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
        pass
