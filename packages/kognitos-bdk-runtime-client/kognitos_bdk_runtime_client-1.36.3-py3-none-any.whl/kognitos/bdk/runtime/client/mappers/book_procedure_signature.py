# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.types.book_procedure_signature_pb2 import \
    BookProcedureSignature as ProtoBookProcedureSignature

from ..book_procedure_signature import BookProcedureSignature
from .noun_phrase import map_noun_phrases


def map_book_procedure_signature(
    data: ProtoBookProcedureSignature,
) -> BookProcedureSignature:
    return BookProcedureSignature(
        english=data.english,
        preposition=data.preposition,
        is_read_only=data.is_read_only,
        verbs=list(data.verbs),
        object=map_noun_phrases(data.object),
        target=map_noun_phrases(data.target),
        outputs=[map_noun_phrases(output) for output in data.outputs],
        proper_nouns=list(data.proper_nouns),
    )
