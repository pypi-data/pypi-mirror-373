from typing import Iterable, List

from ..concept_value import ConceptValue
from ..proto.types.concept_value_pb2 import \
    ConceptValue as ProtoConceptValue  # pylint: disable=no-name-in-module
from . import noun_phrase as noun_phrase_mapper
from . import value as value_mapper


def map_concept_value(value: ProtoConceptValue) -> ConceptValue:
    return ConceptValue(
        noun_phrases=noun_phrase_mapper.map_noun_phrases(value.noun_phrases),
        value=value_mapper.map_value(value.value),
    )


def map_concept_values(values: Iterable[ProtoConceptValue]) -> List[ConceptValue]:
    return list(map(map_concept_value, values))
