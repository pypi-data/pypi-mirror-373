from typing import Any, List, Optional, Tuple

from botocore.config import Config

from . import configs, utils
from .book_descriptor import BookDescriptor
from .book_procedure_descriptor import BookProcedureDescriptor
from .discoverable import Discoverable
from .environment_information import EnvironmentInformation
from .exceptions import TransportBuildError, UnsupportedProtocolVersion
from .expression import Expression
from .grpc_transport import GRPCTransport
from .http_transport import HTTPTransport
from .input_mappers.input_concepts import InputConcept
from .lambda_rie_transport import LambdaRIETransport
from .lambda_transport import LambdaTransport
from .offload import Offload
from .promise import Promise
from .question_answer import AnsweredQuestion
from .request_context import RequestContext
from .transport import InvokeProcedureResponse, Transport


class Client:
    def __init__(self, transport: Transport):
        self.transport = transport

    def retrieve_books(
        self, context: Optional[RequestContext] = None
    ) -> List[BookDescriptor]:
        return self.transport.retrieve_books(context)

    def environment_information(
        self, context: Optional[RequestContext] = None
    ) -> EnvironmentInformation:
        return self.transport.environment_information(context)

    def retrieve_book(
        self, name, version, context: Optional[RequestContext] = None
    ) -> BookDescriptor:
        return self.transport.retrieve_book(name, version, context)

    def retrieve_procedures(
        self,
        name: str,
        version: str,
        include_connect: bool,
        context: Optional[RequestContext] = None,
    ) -> List[BookProcedureDescriptor]:
        return self.transport.retrieve_procedures(
            name, version, include_connect, context
        )

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def test_connection(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str],
        authentication_credentials: Optional[List[Tuple[str, Any]]],
        context: Optional[RequestContext] = None,
    ) -> Any:
        return self.transport.test_connection(
            name, version, authentication_id, authentication_credentials, context
        )

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
        return self.transport.invoke_procedure(
            name,
            version,
            procedure_id,
            authentication_id,
            authentication_credentials,
            input_concepts,
            context,
            filter_expression,
            offload,
            offset,
            limit,
            answered_questions,
        )

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
        return self.transport.discover_procedures(
            name, version, authentication_id, authentication_credentials, what, context
        )

    def retrieve_tags(self, context: Optional[RequestContext] = None) -> List[str]:
        return self.transport.retrieve_tags(context)

    def check_compatibility(self, context: Optional[RequestContext] = None) -> None:
        environment_info = self.environment_information(context)
        proto_version = environment_info.bci_protocol_version
        if not utils.is_bci_protocol_version_supported(proto_version):
            raise UnsupportedProtocolVersion(
                f"The BCI protocol version '{proto_version}' is not supported. The minimum supported version is '{configs.BCI_PROTO_VERSION_FLOOR}'"
            )

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
        return self.transport.retrieve_discoverables(
            name,
            version,
            authentication_id,
            authentication_credentials,
            search,
            limit,
            offset,
            context,
        )

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
        return self.transport.resolve_promise(
            name,
            version,
            procedure_id,
            authentication_id,
            authentication_credentials,
            promise,
            configurations,
            offload,
            answered_questions,
            context,
        )

    @classmethod
    def from_url(
        cls,
        url: str,
        aws_region: Optional[str] = None,
        aws_account_id: Optional[str] = None,
        insecure: bool = False,
        retry_after: float = 10.0,
        lambda_config: Optional[Config] = None,
    ) -> "Client":
        """
        Creates a new client from a `url`. The url needs to have one of three patterns

        Args:
            url: The url of the endpoint to connect to.
            aws_region: The region of the aws account to connect to.
            aws_account_id: The account id of the aws account to connect to.
            insecure: Whether to use an insecure connection. This applies to the http and grpc transports.
            retry_after: The time to wait before retrying a request.
            lambda_config: The config to use for the lambda client. By default we set 0 max attemnts on the lambda client with connect and read timeouts of 15 minutes.

        1) For aws lambdas the pattern has to ve a valid arn:
           `arn:aws:lambda:<aws-region>:<aws-account-id>:function:<aws-lambda-name>`


        2) Another way to make it work for lambdas is to use the `lambda://` url scheme.
           This approach requires the `aws_region` and `aws_account_id` to be provided:

            `lambda://<aws-lambda-name>/<aws-lambda-version>`


        3) For lambda rie, the pattern should follow:
           `lambda+rie://<host>:<port>`

        4) For HTTP/S, in order to establish an http connection, the `insecure` param should be True
            otherwise, we only allow for https. The pattern should follow:

            `http://host:port`      (insecure)
            `https://host:port`
            `http://domain.com`     (insecure)
            `https://domain.com`

        5) For GRPC, the pattern should follow:
            `grpc://host:port`
        """

        try:
            if url.startswith("arn:"):
                return cls(
                    LambdaTransport(
                        url, sleep_retry_time=retry_after, config=lambda_config
                    )
                )

            if url.startswith("lambda://"):
                if not aws_region or not aws_account_id:
                    raise ValueError(
                        "When using the 'lambda://' url scheme, you need to provide the 'aws_region' and 'aws_account_id'"
                    )

                arn = utils.build_lambda_arn(url, aws_region, aws_account_id)
                return cls(
                    LambdaTransport(
                        arn, sleep_retry_time=retry_after, config=lambda_config
                    )
                )

            if url.startswith("lambda+rie://"):
                host, port = utils.get_host_and_port_from_lambda_rie_url(url)
                return cls(LambdaRIETransport(host=host, port=port))

            if url.startswith("http://") or url.startswith("https://"):
                return cls(HTTPTransport(url, insecure))

            if url.startswith("grpc://"):
                grpc_url = utils.build_grpc_url(url)
                return cls(GRPCTransport(grpc_url))

            raise ValueError(
                f"The value of the bdkctl endpoint '{url}' is not correct, please make sure it starts with 'arn:' or 'lambda://' or 'lambda+rie://'"
            )

        except ValueError as exc:
            raise TransportBuildError() from exc
