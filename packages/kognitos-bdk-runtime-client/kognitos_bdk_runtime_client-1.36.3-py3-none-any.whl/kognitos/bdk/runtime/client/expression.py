from dataclasses import dataclass
from enum import Enum
from typing import Union

from .noun_phrase import NounPhrases
from .value import Value


class BinaryOperator(Enum):
    BINARY_OPERATOR_AND = 0
    BINARY_OPERATOR_OR = 1
    BINARY_OPERATOR_EQUALS = 2
    BINARY_OPERATOR_NOT_EQUALS = 3
    BINARY_OPERATOR_IN = 4
    BINARY_OPERATOR_HAS = 5
    BINARY_OPERATOR_LESS_THAN = 6
    BINARY_OPERATOR_GREATER_THAN = 7
    BINARY_OPERATOR_LESS_THAN_OR_EQUAL = 8
    BINARY_OPERATOR_GREATER_THAN_OR_EQUAL = 9


class UnaryOperator(Enum):
    UNARY_OPERATOR_NOT = 0


@dataclass
class BinaryExpression:
    operator: BinaryOperator
    left: "Expression"
    right: "Expression"


@dataclass
class UnaryExpression:
    operator: UnaryOperator
    inner: "Expression"


Expression = Union[BinaryExpression, UnaryExpression, Value, NounPhrases]
