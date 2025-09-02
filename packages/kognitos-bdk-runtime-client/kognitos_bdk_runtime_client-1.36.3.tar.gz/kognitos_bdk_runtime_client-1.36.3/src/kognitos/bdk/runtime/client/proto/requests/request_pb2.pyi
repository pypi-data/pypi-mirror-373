from requests import context_pb2 as _context_pb2
from requests import discover_procedures_pb2 as _discover_procedures_pb2
from requests import environment_information_pb2 as _environment_information_pb2
from requests import invoke_procedure_pb2 as _invoke_procedure_pb2
from requests import resolve_promise_pb2 as _resolve_promise_pb2
from requests import retrieve_book_pb2 as _retrieve_book_pb2
from requests import retrieve_book_procedures_pb2 as _retrieve_book_procedures_pb2
from requests import retrieve_books_pb2 as _retrieve_books_pb2
from requests import retrieve_discoverables_pb2 as _retrieve_discoverables_pb2
from requests import retrieve_tags_pb2 as _retrieve_tags_pb2
from requests import test_connection_pb2 as _test_connection_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Request(_message.Message):
    __slots__ = ('context', 'environment_information', 'retrieve_books', 'retrieve_book', 'retrieve_procedures', 'test_connection', 'invoke_procedure', 'discover_procedures', 'retrieve_discoverables', 'retrieve_tags', 'resolve_promise')
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RETRIEVE_BOOKS_FIELD_NUMBER: _ClassVar[int]
    RETRIEVE_BOOK_FIELD_NUMBER: _ClassVar[int]
    RETRIEVE_PROCEDURES_FIELD_NUMBER: _ClassVar[int]
    TEST_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    INVOKE_PROCEDURE_FIELD_NUMBER: _ClassVar[int]
    DISCOVER_PROCEDURES_FIELD_NUMBER: _ClassVar[int]
    RETRIEVE_DISCOVERABLES_FIELD_NUMBER: _ClassVar[int]
    RETRIEVE_TAGS_FIELD_NUMBER: _ClassVar[int]
    RESOLVE_PROMISE_FIELD_NUMBER: _ClassVar[int]
    context: _context_pb2.Context
    environment_information: _environment_information_pb2.EnvironmentInformationRequest
    retrieve_books: _retrieve_books_pb2.RetrieveBooksRequest
    retrieve_book: _retrieve_book_pb2.RetrieveBookRequest
    retrieve_procedures: _retrieve_book_procedures_pb2.RetrieveBookProceduresRequest
    test_connection: _test_connection_pb2.TestConnectionRequest
    invoke_procedure: _invoke_procedure_pb2.InvokeProcedureRequest
    discover_procedures: _discover_procedures_pb2.DiscoverProceduresRequest
    retrieve_discoverables: _retrieve_discoverables_pb2.RetrieveDiscoverablesRequest
    retrieve_tags: _retrieve_tags_pb2.RetrieveTagsRequest
    resolve_promise: _resolve_promise_pb2.ResolvePromiseRequest

    def __init__(self, context: _Optional[_Union[_context_pb2.Context, _Mapping]]=..., environment_information: _Optional[_Union[_environment_information_pb2.EnvironmentInformationRequest, _Mapping]]=..., retrieve_books: _Optional[_Union[_retrieve_books_pb2.RetrieveBooksRequest, _Mapping]]=..., retrieve_book: _Optional[_Union[_retrieve_book_pb2.RetrieveBookRequest, _Mapping]]=..., retrieve_procedures: _Optional[_Union[_retrieve_book_procedures_pb2.RetrieveBookProceduresRequest, _Mapping]]=..., test_connection: _Optional[_Union[_test_connection_pb2.TestConnectionRequest, _Mapping]]=..., invoke_procedure: _Optional[_Union[_invoke_procedure_pb2.InvokeProcedureRequest, _Mapping]]=..., discover_procedures: _Optional[_Union[_discover_procedures_pb2.DiscoverProceduresRequest, _Mapping]]=..., retrieve_discoverables: _Optional[_Union[_retrieve_discoverables_pb2.RetrieveDiscoverablesRequest, _Mapping]]=..., retrieve_tags: _Optional[_Union[_retrieve_tags_pb2.RetrieveTagsRequest, _Mapping]]=..., resolve_promise: _Optional[_Union[_resolve_promise_pb2.ResolvePromiseRequest, _Mapping]]=...) -> None:
        ...