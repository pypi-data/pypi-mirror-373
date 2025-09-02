# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.types.question_descriptor_pb2 import \
    QuestionDescriptor as ProtoQuestionDescriptor
from kognitos.bdk.runtime.client.question_descriptor import QuestionDescriptor

from . import concept_type as ct
from . import noun_phrase as np


def map_question_descriptor(data: ProtoQuestionDescriptor) -> QuestionDescriptor:
    return QuestionDescriptor(
        noun_phrases=np.map_noun_phrases(data.noun_phrases),
        type=ct.map_concept_type(data.type),
    )
