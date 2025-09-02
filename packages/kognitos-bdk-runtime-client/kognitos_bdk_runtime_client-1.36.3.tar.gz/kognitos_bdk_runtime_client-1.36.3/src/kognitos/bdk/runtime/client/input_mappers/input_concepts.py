from typing import Iterable, List

from ..input_concept import InputConcept
from ..proto.types.concept_value_pb2 import \
    ConceptValue  # pylint: disable=no-name-in-module
from ..proto.types.noun_phrase_pb2 import (  # pylint: disable=no-name-in-module
    NounPhrase, NounPhrases)
from . import value as value_mapper


def _map_concept(concept: InputConcept) -> ConceptValue:
    noun_phrases = concept.noun_phrases.noun_phrases
    value = concept.value

    return ConceptValue(
        noun_phrases=NounPhrases(
            noun_phrases=[
                NounPhrase(head=np.head, modifiers=np.modifiers) for np in noun_phrases
            ]
        ),
        value=value_mapper.map_value(value),
    )


def map_input_concepts(
    input_concepts: List[InputConcept],
) -> Iterable[ConceptValue]:
    return list(map(_map_concept, input_concepts))
