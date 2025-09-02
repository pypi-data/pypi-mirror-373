from kognitos.bdk.runtime.client.concept_descriptor import ConceptDescriptor
# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.types.concept_descriptor_pb2 import \
    ConceptDescriptor as ProtoConceptDescriptor

from . import concept_type as ct
from . import noun_phrase as np
from . import value as v


def map_concept_descriptor(data: ProtoConceptDescriptor) -> ConceptDescriptor:
    return ConceptDescriptor(
        description=data.description,
        type=ct.map_concept_type(data.type),
        noun_phrases=np.map_noun_phrases(data.noun_phrases),
        default_value=v.map_value(data.default_value),
    )
