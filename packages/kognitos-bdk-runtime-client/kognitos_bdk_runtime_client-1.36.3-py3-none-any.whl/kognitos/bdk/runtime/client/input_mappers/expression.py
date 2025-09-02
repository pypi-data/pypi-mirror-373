from typing import Optional

from kognitos.bdk.runtime.client.expression import (BinaryExpression,
                                                    Expression,
                                                    UnaryExpression)
from kognitos.bdk.runtime.client.noun_phrase import NounPhrases
# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.types.expression_pb2 import \
    BinaryExpression as ProtoBinaryExpression
from kognitos.bdk.runtime.client.proto.types.expression_pb2 import \
    BinaryOperator as ProtoBinaryOperator
from kognitos.bdk.runtime.client.proto.types.expression_pb2 import \
    Expression as ProtoExpression
from kognitos.bdk.runtime.client.proto.types.expression_pb2 import \
    UnaryExpression as ProtoUnaryExpression
from kognitos.bdk.runtime.client.proto.types.expression_pb2 import \
    UnaryOperator as ProtoUnaryOperator
from kognitos.bdk.runtime.client.value import Value

from . import noun_phrase as nps_mapper
from . import value as value_mapper


def map_expression(expression: Optional[Expression]) -> Optional[ProtoExpression]:
    def _map_expression_recursive(_expression: Expression) -> ProtoExpression:
        if isinstance(_expression, BinaryExpression):
            return ProtoExpression(
                binary_expression=ProtoBinaryExpression(
                    operator=ProtoBinaryOperator.ValueType(_expression.operator.value),
                    left=_map_expression_recursive(_expression.left),
                    right=_map_expression_recursive(_expression.right),
                )
            )

        if isinstance(_expression, UnaryExpression):
            return ProtoExpression(
                unary_expression=ProtoUnaryExpression(
                    operator=ProtoUnaryOperator.ValueType(_expression.operator.value),
                    inner=_map_expression_recursive(_expression.inner),
                )
            )

        # NOTE: Doing Value.__args__ in order to be compatible with python3.9. In newer versions of python
        # we can use isinstance(_expression, Value) directly.
        if isinstance(_expression, Value.__args__):
            # fmt: off
            return ProtoExpression(
                value_expression=value_mapper.map_value(_expression) # pyright: ignore [reportArgumentType]
            )
            # fmt: on

        if isinstance(_expression, NounPhrases):
            return ProtoExpression(
                noun_phrases_expression=nps_mapper.map_noun_phrases(_expression)
            )

        raise ValueError(f"Unknown expression type: {_expression}")

    if expression:
        return _map_expression_recursive(expression)
    return None
