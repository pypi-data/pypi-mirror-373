"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from ..requests import add_book_instance_pb2 as requests_dot_add__book__instance__pb2
from ..requests import discover_procedures_pb2 as requests_dot_discover__procedures__pb2
from ..requests import environment_information_pb2 as requests_dot_environment__information__pb2
from ..requests import invoke_procedure_pb2 as requests_dot_invoke__procedure__pb2
from ..requests import remove_book_instance_pb2 as requests_dot_remove__book__instance__pb2
from ..requests import retrieve_book_pb2 as requests_dot_retrieve__book__pb2
from ..requests import retrieve_book_procedures_pb2 as requests_dot_retrieve__book__procedures__pb2
from ..requests import retrieve_books_pb2 as requests_dot_retrieve__books__pb2
from ..requests import retrieve_tags_pb2 as requests_dot_retrieve__tags__pb2
from ..requests import test_connection_pb2 as requests_dot_test__connection__pb2
from ..responses import add_book_instance_pb2 as responses_dot_add__book__instance__pb2
from ..responses import discover_procedures_pb2 as responses_dot_discover__procedures__pb2
from ..responses import environment_information_pb2 as responses_dot_environment__information__pb2
from ..responses import invoke_procedure_pb2 as responses_dot_invoke__procedure__pb2
from ..responses import remove_book_instance_pb2 as responses_dot_remove__book__instance__pb2
from ..responses import retrieve_book_pb2 as responses_dot_retrieve__book__pb2
from ..responses import retrieve_book_procedures_pb2 as responses_dot_retrieve__book__procedures__pb2
from ..responses import retrieve_books_pb2 as responses_dot_retrieve__books__pb2
from ..responses import retrieve_tags_pb2 as responses_dot_retrieve__tags__pb2
from ..responses import test_connection_pb2 as responses_dot_test__connection__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16services/library.proto\x12\x08protocol\x1a\x1cgoogle/api/annotations.proto\x1a requests/add_book_instance.proto\x1a"requests/discover_procedures.proto\x1a&requests/environment_information.proto\x1a\x1frequests/invoke_procedure.proto\x1a#requests/remove_book_instance.proto\x1a\x1crequests/retrieve_book.proto\x1a\'requests/retrieve_book_procedures.proto\x1a\x1drequests/retrieve_books.proto\x1a\x1crequests/retrieve_tags.proto\x1a\x1erequests/test_connection.proto\x1a!responses/add_book_instance.proto\x1a#responses/discover_procedures.proto\x1a\'responses/environment_information.proto\x1a responses/invoke_procedure.proto\x1a$responses/remove_book_instance.proto\x1a\x1dresponses/retrieve_book.proto\x1a(responses/retrieve_book_procedures.proto\x1a\x1eresponses/retrieve_books.proto\x1a\x1dresponses/retrieve_tags.proto\x1a\x1fresponses/test_connection.proto2\xda\x07\n\x0eLibraryService\x12g\n\rRetrieveBooks\x12\x1e.protocol.RetrieveBooksRequest\x1a\x1f.protocol.RetrieveBooksResponse"\x15\x82\xd3\xe4\x93\x02\x0f\x12\r/api/v1/books\x12u\n\x0cRetrieveBook\x12\x1d.protocol.RetrieveBookRequest\x1a\x1e.protocol.RetrieveBookResponse"&\x82\xd3\xe4\x93\x02 \x12\x1e/api/v1/books/{name}/{version}\x12\xa0\x01\n\x16RetrieveBookProcedures\x12\'.protocol.RetrieveBookProceduresRequest\x1a*.protocol.RetrieveBookProceduresResponseV2"1\x82\xd3\xe4\x93\x02+\x12)/api/v1/books/{name}/{version}/procedures\x12\x9b\x01\n\x0eTestConnection\x12\x1f.protocol.TestConnectionRequest\x1a .protocol.TestConnectionResponse"F\x82\xd3\xe4\x93\x02@"./api/v1/books/{name}/{version}/test-connection:\x0eauthentication\x12c\n\x0cRetrieveTags\x12\x1d.protocol.RetrieveTagsRequest\x1a\x1e.protocol.RetrieveTagsResponse"\x14\x82\xd3\xe4\x93\x02\x0e\x12\x0c/api/v1/tags\x12\x95\x01\n\x0fAddBookInstance\x12 .protocol.AddBookInstanceRequest\x1a!.protocol.AddBookInstanceResponse"=\x82\xd3\xe4\x93\x027"2/api/v1/books/{book_name}/{book_version}/instances:\x01*\x12\xa9\x01\n\x12RemoveBookInstance\x12#.protocol.RemoveBookInstanceRequest\x1a$.protocol.RemoveBookInstanceResponse"H\x82\xd3\xe4\x93\x02B*@/api/v1/books/{book_name}/{book_version}/instances/{instance_id}B\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.library_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_LIBRARYSERVICE'].methods_by_name['RetrieveBooks']._options = None
    _globals['_LIBRARYSERVICE'].methods_by_name['RetrieveBooks']._serialized_options = b'\x82\xd3\xe4\x93\x02\x0f\x12\r/api/v1/books'
    _globals['_LIBRARYSERVICE'].methods_by_name['RetrieveBook']._options = None
    _globals['_LIBRARYSERVICE'].methods_by_name['RetrieveBook']._serialized_options = b'\x82\xd3\xe4\x93\x02 \x12\x1e/api/v1/books/{name}/{version}'
    _globals['_LIBRARYSERVICE'].methods_by_name['RetrieveBookProcedures']._options = None
    _globals['_LIBRARYSERVICE'].methods_by_name['RetrieveBookProcedures']._serialized_options = b'\x82\xd3\xe4\x93\x02+\x12)/api/v1/books/{name}/{version}/procedures'
    _globals['_LIBRARYSERVICE'].methods_by_name['TestConnection']._options = None
    _globals['_LIBRARYSERVICE'].methods_by_name['TestConnection']._serialized_options = b'\x82\xd3\xe4\x93\x02@"./api/v1/books/{name}/{version}/test-connection:\x0eauthentication'
    _globals['_LIBRARYSERVICE'].methods_by_name['RetrieveTags']._options = None
    _globals['_LIBRARYSERVICE'].methods_by_name['RetrieveTags']._serialized_options = b'\x82\xd3\xe4\x93\x02\x0e\x12\x0c/api/v1/tags'
    _globals['_LIBRARYSERVICE'].methods_by_name['AddBookInstance']._options = None
    _globals['_LIBRARYSERVICE'].methods_by_name['AddBookInstance']._serialized_options = b'\x82\xd3\xe4\x93\x027"2/api/v1/books/{book_name}/{book_version}/instances:\x01*'
    _globals['_LIBRARYSERVICE'].methods_by_name['RemoveBookInstance']._options = None
    _globals['_LIBRARYSERVICE'].methods_by_name['RemoveBookInstance']._serialized_options = b'\x82\xd3\xe4\x93\x02B*@/api/v1/books/{book_name}/{book_version}/instances/{instance_id}'
    _globals['_LIBRARYSERVICE']._serialized_start = 765
    _globals['_LIBRARYSERVICE']._serialized_end = 1751