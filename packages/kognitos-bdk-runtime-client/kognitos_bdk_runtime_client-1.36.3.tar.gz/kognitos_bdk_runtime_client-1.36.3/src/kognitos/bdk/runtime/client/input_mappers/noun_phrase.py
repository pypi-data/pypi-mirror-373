from kognitos.bdk.runtime.client.noun_phrase import NounPhrase, NounPhrases
# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.types.noun_phrase_pb2 import \
    NounPhrase as ProtoNounPhrase
from kognitos.bdk.runtime.client.proto.types.noun_phrase_pb2 import \
    NounPhrases as ProtoNounPhrases


def map_noun_phrase(noun_phrase: NounPhrase) -> ProtoNounPhrase:
    return ProtoNounPhrase(
        modifiers=noun_phrase.modifiers,
        head=noun_phrase.head,
    )


def map_noun_phrases(noun_phrases: NounPhrases) -> ProtoNounPhrases:
    return ProtoNounPhrases(
        noun_phrases=[
            map_noun_phrase(noun_phrase) for noun_phrase in noun_phrases.noun_phrases
        ]
    )
