from responses import discover_procedures_pb2 as _discover_procedures_pb2
from responses import environment_information_pb2 as _environment_information_pb2
from responses import error_pb2 as _error_pb2
from responses import invoke_procedure_pb2 as _invoke_procedure_pb2
from responses import promise_pb2 as _promise_pb2
from responses import question_pb2 as _question_pb2
from responses import retrieve_book_pb2 as _retrieve_book_pb2
from responses import retrieve_book_procedures_pb2 as _retrieve_book_procedures_pb2
from responses import retrieve_books_pb2 as _retrieve_books_pb2
from responses import retrieve_discoverables_pb2 as _retrieve_discoverables_pb2
from responses import retrieve_tags_pb2 as _retrieve_tags_pb2
from responses import test_connection_pb2 as _test_connection_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ('error', 'environment_information', 'retrieved_books', 'retrieved_book', 'retrieved_procedures', 'tested_connection', 'invoked_procedure', 'discovered_procedures', 'question', 'retrieved_discoverables', 'retrieved_tags', 'promise')
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RETRIEVED_BOOKS_FIELD_NUMBER: _ClassVar[int]
    RETRIEVED_BOOK_FIELD_NUMBER: _ClassVar[int]
    RETRIEVED_PROCEDURES_FIELD_NUMBER: _ClassVar[int]
    TESTED_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    INVOKED_PROCEDURE_FIELD_NUMBER: _ClassVar[int]
    DISCOVERED_PROCEDURES_FIELD_NUMBER: _ClassVar[int]
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    RETRIEVED_DISCOVERABLES_FIELD_NUMBER: _ClassVar[int]
    RETRIEVED_TAGS_FIELD_NUMBER: _ClassVar[int]
    PROMISE_FIELD_NUMBER: _ClassVar[int]
    error: _error_pb2.Error
    environment_information: _environment_information_pb2.EnvironmentInformationResponse
    retrieved_books: _retrieve_books_pb2.RetrieveBooksResponse
    retrieved_book: _retrieve_book_pb2.RetrieveBookResponse
    retrieved_procedures: _retrieve_book_procedures_pb2.RetrieveBookProceduresResponse
    tested_connection: _test_connection_pb2.TestConnectionResponse
    invoked_procedure: _invoke_procedure_pb2.InvokeProcedureResponse
    discovered_procedures: _discover_procedures_pb2.DiscoverProceduresResponse
    question: _question_pb2.QuestionResponse
    retrieved_discoverables: _retrieve_discoverables_pb2.RetrieveDiscoverablesResponse
    retrieved_tags: _retrieve_tags_pb2.RetrieveTagsResponse
    promise: _promise_pb2.PromiseResponse

    def __init__(self, error: _Optional[_Union[_error_pb2.Error, _Mapping]]=..., environment_information: _Optional[_Union[_environment_information_pb2.EnvironmentInformationResponse, _Mapping]]=..., retrieved_books: _Optional[_Union[_retrieve_books_pb2.RetrieveBooksResponse, _Mapping]]=..., retrieved_book: _Optional[_Union[_retrieve_book_pb2.RetrieveBookResponse, _Mapping]]=..., retrieved_procedures: _Optional[_Union[_retrieve_book_procedures_pb2.RetrieveBookProceduresResponse, _Mapping]]=..., tested_connection: _Optional[_Union[_test_connection_pb2.TestConnectionResponse, _Mapping]]=..., invoked_procedure: _Optional[_Union[_invoke_procedure_pb2.InvokeProcedureResponse, _Mapping]]=..., discovered_procedures: _Optional[_Union[_discover_procedures_pb2.DiscoverProceduresResponse, _Mapping]]=..., question: _Optional[_Union[_question_pb2.QuestionResponse, _Mapping]]=..., retrieved_discoverables: _Optional[_Union[_retrieve_discoverables_pb2.RetrieveDiscoverablesResponse, _Mapping]]=..., retrieved_tags: _Optional[_Union[_retrieve_tags_pb2.RetrieveTagsResponse, _Mapping]]=..., promise: _Optional[_Union[_promise_pb2.PromiseResponse, _Mapping]]=...) -> None:
        ...