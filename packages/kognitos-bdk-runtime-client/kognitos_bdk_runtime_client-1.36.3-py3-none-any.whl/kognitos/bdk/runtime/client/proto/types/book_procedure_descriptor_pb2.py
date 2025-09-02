"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import book_procedure_signature_pb2 as types_dot_book__procedure__signature__pb2
from ..types import concept_descriptor_pb2 as types_dot_concept__descriptor__pb2
from ..types import connection_required_pb2 as types_dot_connection__required__pb2
from ..types import example_descriptor_pb2 as types_dot_example__descriptor__pb2
from ..types import question_descriptor_pb2 as types_dot_question__descriptor__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%types/book_procedure_descriptor.proto\x12\x08protocol\x1a$types/book_procedure_signature.proto\x1a\x1etypes/concept_descriptor.proto\x1a\x1ftypes/connection_required.proto\x1a\x1etypes/example_descriptor.proto\x1a\x1ftypes/question_descriptor.proto"\xf6\x05\n\x17BookProcedureDescriptor\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12>\n\tsignature\x18\x02 \x01(\x0b2 .protocol.BookProcedureSignatureR\tsignature\x123\n\x06inputs\x18\x03 \x03(\x0b2\x1b.protocol.ConceptDescriptorR\x06inputs\x125\n\x07outputs\x18\x04 \x03(\x0b2\x1b.protocol.ConceptDescriptorR\x07outputs\x120\n\x11short_description\x18\x05 \x01(\tH\x00R\x10shortDescription\x88\x01\x01\x12.\n\x10long_description\x18\x06 \x01(\tH\x01R\x0flongDescription\x88\x01\x01\x12%\n\x0efilter_capable\x18\x07 \x01(\x08R\rfilterCapable\x12!\n\x0cpage_capable\x18\x08 \x01(\x08R\x0bpageCapable\x123\n\x13connection_required\x18\t \x01(\x08B\x02\x18\x01R\x12connectionRequired\x12#\n\ris_discovered\x18\n \x01(\x08R\x0cisDiscovered\x12:\n\tquestions\x18\x0b \x03(\x0b2\x1c.protocol.QuestionDescriptorR\tquestions\x127\n\x08examples\x18\x0c \x03(\x0b2\x1b.protocol.ExampleDescriptorR\x08examples\x12\x19\n\x08is_async\x18\r \x01(\x08R\x07isAsync\x12^\n\x1cconnection_requirement_level\x18\x0e \x01(\x0e2\x1c.protocol.ConnectionRequiredR\x1aconnectionRequirementLevelB\x14\n\x12_short_descriptionB\x13\n\x11_long_description"\xb2\x05\n\x19BookProcedureDescriptorV2\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12>\n\tsignature\x18\x02 \x01(\x0b2 .protocol.BookProcedureSignatureR\tsignature\x123\n\x06inputs\x18\x03 \x03(\x0b2\x1b.protocol.ConceptDescriptorR\x06inputs\x125\n\x07outputs\x18\x04 \x03(\x0b2\x1b.protocol.ConceptDescriptorR\x07outputs\x120\n\x11short_description\x18\x05 \x01(\tH\x00R\x10shortDescription\x88\x01\x01\x12.\n\x10long_description\x18\x06 \x01(\tH\x01R\x0flongDescription\x88\x01\x01\x12%\n\x0efilter_capable\x18\x07 \x01(\x08R\rfilterCapable\x12!\n\x0cpage_capable\x18\x08 \x01(\x08R\x0bpageCapable\x12M\n\x13connection_required\x18\t \x01(\x0e2\x1c.protocol.ConnectionRequiredR\x12connectionRequired\x12#\n\ris_discovered\x18\n \x01(\x08R\x0cisDiscovered\x12:\n\tquestions\x18\x0b \x03(\x0b2\x1c.protocol.QuestionDescriptorR\tquestions\x127\n\x08examples\x18\x0c \x03(\x0b2\x1b.protocol.ExampleDescriptorR\x08examples\x12\x19\n\x08is_async\x18\r \x01(\x08R\x07isAsyncB\x14\n\x12_short_descriptionB\x13\n\x11_long_descriptionB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.book_procedure_descriptor_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_BOOKPROCEDUREDESCRIPTOR'].fields_by_name['connection_required']._options = None
    _globals['_BOOKPROCEDUREDESCRIPTOR'].fields_by_name['connection_required']._serialized_options = b'\x18\x01'
    _globals['_BOOKPROCEDUREDESCRIPTOR']._serialized_start = 220
    _globals['_BOOKPROCEDUREDESCRIPTOR']._serialized_end = 978
    _globals['_BOOKPROCEDUREDESCRIPTORV2']._serialized_start = 981
    _globals['_BOOKPROCEDUREDESCRIPTORV2']._serialized_end = 1671