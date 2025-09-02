from typing import Iterable, List

from kognitos.bdk.runtime.client.question_answer import AnsweredQuestion

# pylint: disable=no-name-in-module
from ..proto.types.answered_question_pb2 import \
    AnsweredQuestion as ProtoAnsweredQuestion
from .noun_phrase import map_noun_phrases
from .value import map_value


def _map_answered_question(
    answered_question: AnsweredQuestion,
) -> ProtoAnsweredQuestion:
    return ProtoAnsweredQuestion(
        noun_phrases=map_noun_phrases(answered_question.noun_phrases),
        answer=map_value(answered_question.answer),
    )


def map_answered_questions(
    answered_questions: List[AnsweredQuestion],
) -> Iterable[ProtoAnsweredQuestion]:
    return list(map(_map_answered_question, answered_questions))
