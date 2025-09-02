# pylint: disable=no-name-in-module
from typing import Iterable, List

from kognitos.bdk.runtime.client.proto.types.question_pb2 import \
    Question as ProtoQuestion
from kognitos.bdk.runtime.client.question_answer import Question

from . import concept_type as concept_type_mapper
from . import noun_phrase as noun_phrase_mapper
from . import value as value_mapper


def map_question(data: ProtoQuestion) -> Question:
    choices = (
        [value_mapper.map_value(choice) for choice in data.choices]
        if data.choices
        else None
    )
    return Question(
        noun_phrases=noun_phrase_mapper.map_noun_phrases(data.noun_phrases),
        concept_type=concept_type_mapper.map_concept_type(data.concept_type),
        choices=choices,
        text=data.text if data.HasField("text") else None,
    )


def map_questions(data: Iterable[ProtoQuestion]) -> List[Question]:
    return list(map(map_question, data))
