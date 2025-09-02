"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..requests import discover_procedures_pb2 as requests_dot_discover__procedures__pb2
from ..requests import environment_information_pb2 as requests_dot_environment__information__pb2
from ..requests import invoke_procedure_pb2 as requests_dot_invoke__procedure__pb2
from ..requests import resolve_promise_pb2 as requests_dot_resolve__promise__pb2
from ..requests import retrieve_book_pb2 as requests_dot_retrieve__book__pb2
from ..requests import retrieve_book_procedures_pb2 as requests_dot_retrieve__book__procedures__pb2
from ..requests import retrieve_books_pb2 as requests_dot_retrieve__books__pb2
from ..requests import retrieve_discoverables_pb2 as requests_dot_retrieve__discoverables__pb2
from ..requests import test_connection_pb2 as requests_dot_test__connection__pb2
from ..responses import discover_procedures_pb2 as responses_dot_discover__procedures__pb2
from ..responses import environment_information_pb2 as responses_dot_environment__information__pb2
from ..responses import invoke_procedure_pb2 as responses_dot_invoke__procedure__pb2
from ..responses import retrieve_book_pb2 as responses_dot_retrieve__book__pb2
from ..responses import retrieve_book_procedures_pb2 as responses_dot_retrieve__book__procedures__pb2
from ..responses import retrieve_books_pb2 as responses_dot_retrieve__books__pb2
from ..responses import retrieve_discoverables_pb2 as responses_dot_retrieve__discoverables__pb2
from ..responses import test_connection_pb2 as responses_dot_test__connection__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13services/book.proto\x12\x08protocol\x1a"requests/discover_procedures.proto\x1a&requests/environment_information.proto\x1a\x1frequests/invoke_procedure.proto\x1a\x1erequests/resolve_promise.proto\x1a\x1crequests/retrieve_book.proto\x1a\'requests/retrieve_book_procedures.proto\x1a\x1drequests/retrieve_books.proto\x1a%requests/retrieve_discoverables.proto\x1a\x1erequests/test_connection.proto\x1a#responses/discover_procedures.proto\x1a\'responses/environment_information.proto\x1a responses/invoke_procedure.proto\x1a\x1dresponses/retrieve_book.proto\x1a(responses/retrieve_book_procedures.proto\x1a\x1eresponses/retrieve_books.proto\x1a&responses/retrieve_discoverables.proto\x1a\x1fresponses/test_connection.proto2\xdc\x06\n\x0bBookService\x12k\n\x16EnvironmentInformation\x12\'.protocol.EnvironmentInformationRequest\x1a(.protocol.EnvironmentInformationResponse\x12P\n\rRetrieveBooks\x12\x1e.protocol.RetrieveBooksRequest\x1a\x1f.protocol.RetrieveBooksResponse\x12M\n\x0cRetrieveBook\x12\x1d.protocol.RetrieveBookRequest\x1a\x1e.protocol.RetrieveBookResponse\x12m\n\x16RetrieveBookProcedures\x12\'.protocol.RetrieveBookProceduresRequest\x1a*.protocol.RetrieveBookProceduresResponseV2\x12S\n\x0eTestConnection\x12\x1f.protocol.TestConnectionRequest\x1a .protocol.TestConnectionResponse\x12X\n\x0fInvokeProcedure\x12 .protocol.InvokeProcedureRequest\x1a#.protocol.InvokeProcedureResponseV2\x12_\n\x12DiscoverProcedures\x12#.protocol.DiscoverProceduresRequest\x1a$.protocol.DiscoverProceduresResponse\x12h\n\x15RetrieveDiscoverables\x12&.protocol.RetrieveDiscoverablesRequest\x1a\'.protocol.RetrieveDiscoverablesResponse\x12V\n\x0eResolvePromise\x12\x1f.protocol.ResolvePromiseRequest\x1a#.protocol.InvokeProcedureResponseV2B\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'services.book_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_BOOKSERVICE']._serialized_start = 638
    _globals['_BOOKSERVICE']._serialized_end = 1498