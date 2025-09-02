"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..requests import context_pb2 as requests_dot_context__pb2
from ..requests import discover_procedures_pb2 as requests_dot_discover__procedures__pb2
from ..requests import environment_information_pb2 as requests_dot_environment__information__pb2
from ..requests import invoke_procedure_pb2 as requests_dot_invoke__procedure__pb2
from ..requests import resolve_promise_pb2 as requests_dot_resolve__promise__pb2
from ..requests import retrieve_book_pb2 as requests_dot_retrieve__book__pb2
from ..requests import retrieve_book_procedures_pb2 as requests_dot_retrieve__book__procedures__pb2
from ..requests import retrieve_books_pb2 as requests_dot_retrieve__books__pb2
from ..requests import retrieve_discoverables_pb2 as requests_dot_retrieve__discoverables__pb2
from ..requests import retrieve_tags_pb2 as requests_dot_retrieve__tags__pb2
from ..requests import test_connection_pb2 as requests_dot_test__connection__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16requests/request.proto\x12\x08protocol\x1a\x16requests/context.proto\x1a"requests/discover_procedures.proto\x1a&requests/environment_information.proto\x1a\x1frequests/invoke_procedure.proto\x1a\x1erequests/resolve_promise.proto\x1a\x1crequests/retrieve_book.proto\x1a\'requests/retrieve_book_procedures.proto\x1a\x1drequests/retrieve_books.proto\x1a%requests/retrieve_discoverables.proto\x1a\x1crequests/retrieve_tags.proto\x1a\x1erequests/test_connection.proto"\x84\x07\n\x07Request\x12+\n\x07context\x18\x01 \x01(\x0b2\x11.protocol.ContextR\x07context\x12b\n\x17environment_information\x18\x02 \x01(\x0b2\'.protocol.EnvironmentInformationRequestH\x00R\x16environmentInformation\x12G\n\x0eretrieve_books\x18\x03 \x01(\x0b2\x1e.protocol.RetrieveBooksRequestH\x00R\rretrieveBooks\x12D\n\rretrieve_book\x18\x04 \x01(\x0b2\x1d.protocol.RetrieveBookRequestH\x00R\x0cretrieveBook\x12Z\n\x13retrieve_procedures\x18\x05 \x01(\x0b2\'.protocol.RetrieveBookProceduresRequestH\x00R\x12retrieveProcedures\x12J\n\x0ftest_connection\x18\x06 \x01(\x0b2\x1f.protocol.TestConnectionRequestH\x00R\x0etestConnection\x12M\n\x10invoke_procedure\x18\x07 \x01(\x0b2 .protocol.InvokeProcedureRequestH\x00R\x0finvokeProcedure\x12V\n\x13discover_procedures\x18\x08 \x01(\x0b2#.protocol.DiscoverProceduresRequestH\x00R\x12discoverProcedures\x12_\n\x16retrieve_discoverables\x18\t \x01(\x0b2&.protocol.RetrieveDiscoverablesRequestH\x00R\x15retrieveDiscoverables\x12D\n\rretrieve_tags\x18\n \x01(\x0b2\x1d.protocol.RetrieveTagsRequestH\x00R\x0cretrieveTags\x12J\n\x0fresolve_promise\x18\x0b \x01(\x0b2\x1f.protocol.ResolvePromiseRequestH\x00R\x0eresolvePromiseB\x17\n\x15request_discriminatorB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'requests.request_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_REQUEST']._serialized_start = 405
    _globals['_REQUEST']._serialized_end = 1305