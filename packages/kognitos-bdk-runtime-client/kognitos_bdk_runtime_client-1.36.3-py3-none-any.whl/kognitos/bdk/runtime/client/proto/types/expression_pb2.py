"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import noun_phrase_pb2 as types_dot_noun__phrase__pb2
from ..types import value_pb2 as types_dot_value__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16types/expression.proto\x12\x08protocol\x1a\x17types/noun_phrase.proto\x1a\x11types/value.proto"\xbc\x02\n\nExpression\x12I\n\x11binary_expression\x18\x01 \x01(\x0b2\x1a.protocol.BinaryExpressionH\x00R\x10binaryExpression\x12F\n\x10unary_expression\x18\x02 \x01(\x0b2\x19.protocol.UnaryExpressionH\x00R\x0funaryExpression\x12<\n\x10value_expression\x18\x03 \x01(\x0b2\x0f.protocol.ValueH\x00R\x0fvalueExpression\x12O\n\x17noun_phrases_expression\x18\x04 \x01(\x0b2\x15.protocol.NounPhrasesH\x00R\x15nounPhrasesExpressionB\x0c\n\nexpression"\x9e\x01\n\x10BinaryExpression\x124\n\x08operator\x18\x01 \x01(\x0e2\x18.protocol.BinaryOperatorR\x08operator\x12(\n\x04left\x18\x02 \x01(\x0b2\x14.protocol.ExpressionR\x04left\x12*\n\x05right\x18\x03 \x01(\x0b2\x14.protocol.ExpressionR\x05right"r\n\x0fUnaryExpression\x123\n\x08operator\x18\x01 \x01(\x0e2\x17.protocol.UnaryOperatorR\x08operator\x12*\n\x05inner\x18\x02 \x01(\x0b2\x14.protocol.ExpressionR\x05inner*\xa5\x02\n\x0eBinaryOperator\x12\x15\n\x11BinaryOperatorAnd\x10\x00\x12\x14\n\x10BinaryOperatorOr\x10\x01\x12\x18\n\x14BinaryOperatorEquals\x10\x02\x12\x1b\n\x17BinaryOperatorNotEquals\x10\x03\x12\x14\n\x10BinaryOperatorIn\x10\x04\x12\x15\n\x11BinaryOperatorHas\x10\x05\x12\x1a\n\x16BinaryOperatorLessThan\x10\x06\x12\x1d\n\x19BinaryOperatorGreaterThan\x10\x07\x12!\n\x1dBinaryOperatorLessThanOrEqual\x10\x08\x12$\n BinaryOperatorGreaterThanOrEqual\x10\t*%\n\rUnaryOperator\x12\x14\n\x10UnaryOperatorNot\x10\x00B\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.expression_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_BINARYOPERATOR']._serialized_start = 677
    _globals['_BINARYOPERATOR']._serialized_end = 970
    _globals['_UNARYOPERATOR']._serialized_start = 972
    _globals['_UNARYOPERATOR']._serialized_end = 1009
    _globals['_EXPRESSION']._serialized_start = 81
    _globals['_EXPRESSION']._serialized_end = 397
    _globals['_BINARYEXPRESSION']._serialized_start = 400
    _globals['_BINARYEXPRESSION']._serialized_end = 558
    _globals['_UNARYEXPRESSION']._serialized_start = 560
    _globals['_UNARYEXPRESSION']._serialized_end = 674