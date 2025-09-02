"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..responses import discover_procedures_pb2 as responses_dot_discover__procedures__pb2
from ..responses import environment_information_pb2 as responses_dot_environment__information__pb2
from ..responses import error_pb2 as responses_dot_error__pb2
from ..responses import invoke_procedure_pb2 as responses_dot_invoke__procedure__pb2
from ..responses import promise_pb2 as responses_dot_promise__pb2
from ..responses import question_pb2 as responses_dot_question__pb2
from ..responses import retrieve_book_pb2 as responses_dot_retrieve__book__pb2
from ..responses import retrieve_book_procedures_pb2 as responses_dot_retrieve__book__procedures__pb2
from ..responses import retrieve_books_pb2 as responses_dot_retrieve__books__pb2
from ..responses import retrieve_discoverables_pb2 as responses_dot_retrieve__discoverables__pb2
from ..responses import retrieve_tags_pb2 as responses_dot_retrieve__tags__pb2
from ..responses import test_connection_pb2 as responses_dot_test__connection__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18responses/response.proto\x12\x08protocol\x1a#responses/discover_procedures.proto\x1a\'responses/environment_information.proto\x1a\x15responses/error.proto\x1a responses/invoke_procedure.proto\x1a\x17responses/promise.proto\x1a\x18responses/question.proto\x1a\x1dresponses/retrieve_book.proto\x1a(responses/retrieve_book_procedures.proto\x1a\x1eresponses/retrieve_books.proto\x1a&responses/retrieve_discoverables.proto\x1a\x1dresponses/retrieve_tags.proto\x1a\x1fresponses/test_connection.proto"\xc4\x07\n\x08Response\x12\'\n\x05error\x18\x01 \x01(\x0b2\x0f.protocol.ErrorH\x00R\x05error\x12c\n\x17environment_information\x18\x02 \x01(\x0b2(.protocol.EnvironmentInformationResponseH\x00R\x16environmentInformation\x12J\n\x0fretrieved_books\x18\x03 \x01(\x0b2\x1f.protocol.RetrieveBooksResponseH\x00R\x0eretrievedBooks\x12G\n\x0eretrieved_book\x18\x04 \x01(\x0b2\x1e.protocol.RetrieveBookResponseH\x00R\rretrievedBook\x12]\n\x14retrieved_procedures\x18\x05 \x01(\x0b2(.protocol.RetrieveBookProceduresResponseH\x00R\x13retrievedProcedures\x12O\n\x11tested_connection\x18\x06 \x01(\x0b2 .protocol.TestConnectionResponseH\x00R\x10testedConnection\x12P\n\x11invoked_procedure\x18\x07 \x01(\x0b2!.protocol.InvokeProcedureResponseH\x00R\x10invokedProcedure\x12[\n\x15discovered_procedures\x18\x08 \x01(\x0b2$.protocol.DiscoverProceduresResponseH\x00R\x14discoveredProcedures\x128\n\x08question\x18\t \x01(\x0b2\x1a.protocol.QuestionResponseH\x00R\x08question\x12b\n\x17retrieved_discoverables\x18\n \x01(\x0b2\'.protocol.RetrieveDiscoverablesResponseH\x00R\x16retrievedDiscoverables\x12G\n\x0eretrieved_tags\x18\x0b \x01(\x0b2\x1e.protocol.RetrieveTagsResponseH\x00R\rretrievedTags\x125\n\x07promise\x18\x0c \x01(\x0b2\x19.protocol.PromiseResponseH\x00R\x07promiseB\x18\n\x16response_discriminatorB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.response_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_RESPONSE']._serialized_start = 434
    _globals['_RESPONSE']._serialized_end = 1398