from types import noun_phrase_pb2 as _noun_phrase_pb2
from types import value_pb2 as _value_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class BinaryOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BinaryOperatorAnd: _ClassVar[BinaryOperator]
    BinaryOperatorOr: _ClassVar[BinaryOperator]
    BinaryOperatorEquals: _ClassVar[BinaryOperator]
    BinaryOperatorNotEquals: _ClassVar[BinaryOperator]
    BinaryOperatorIn: _ClassVar[BinaryOperator]
    BinaryOperatorHas: _ClassVar[BinaryOperator]
    BinaryOperatorLessThan: _ClassVar[BinaryOperator]
    BinaryOperatorGreaterThan: _ClassVar[BinaryOperator]
    BinaryOperatorLessThanOrEqual: _ClassVar[BinaryOperator]
    BinaryOperatorGreaterThanOrEqual: _ClassVar[BinaryOperator]

class UnaryOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UnaryOperatorNot: _ClassVar[UnaryOperator]
BinaryOperatorAnd: BinaryOperator
BinaryOperatorOr: BinaryOperator
BinaryOperatorEquals: BinaryOperator
BinaryOperatorNotEquals: BinaryOperator
BinaryOperatorIn: BinaryOperator
BinaryOperatorHas: BinaryOperator
BinaryOperatorLessThan: BinaryOperator
BinaryOperatorGreaterThan: BinaryOperator
BinaryOperatorLessThanOrEqual: BinaryOperator
BinaryOperatorGreaterThanOrEqual: BinaryOperator
UnaryOperatorNot: UnaryOperator

class Expression(_message.Message):
    __slots__ = ('binary_expression', 'unary_expression', 'value_expression', 'noun_phrases_expression')
    BINARY_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    UNARY_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    VALUE_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    NOUN_PHRASES_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    binary_expression: BinaryExpression
    unary_expression: UnaryExpression
    value_expression: _value_pb2.Value
    noun_phrases_expression: _noun_phrase_pb2.NounPhrases

    def __init__(self, binary_expression: _Optional[_Union[BinaryExpression, _Mapping]]=..., unary_expression: _Optional[_Union[UnaryExpression, _Mapping]]=..., value_expression: _Optional[_Union[_value_pb2.Value, _Mapping]]=..., noun_phrases_expression: _Optional[_Union[_noun_phrase_pb2.NounPhrases, _Mapping]]=...) -> None:
        ...

class BinaryExpression(_message.Message):
    __slots__ = ('operator', 'left', 'right')
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    LEFT_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FIELD_NUMBER: _ClassVar[int]
    operator: BinaryOperator
    left: Expression
    right: Expression

    def __init__(self, operator: _Optional[_Union[BinaryOperator, str]]=..., left: _Optional[_Union[Expression, _Mapping]]=..., right: _Optional[_Union[Expression, _Mapping]]=...) -> None:
        ...

class UnaryExpression(_message.Message):
    __slots__ = ('operator', 'inner')
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    INNER_FIELD_NUMBER: _ClassVar[int]
    operator: UnaryOperator
    inner: Expression

    def __init__(self, operator: _Optional[_Union[UnaryOperator, str]]=..., inner: _Optional[_Union[Expression, _Mapping]]=...) -> None:
        ...