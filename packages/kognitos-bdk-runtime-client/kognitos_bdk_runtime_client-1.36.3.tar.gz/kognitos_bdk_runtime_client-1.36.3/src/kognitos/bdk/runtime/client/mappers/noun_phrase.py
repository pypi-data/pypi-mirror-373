from kognitos.bdk.runtime.client.noun_phrase import NounPhrase, NounPhrases


def map_noun_phrase(data) -> NounPhrase:
    return NounPhrase(head=data.head, modifiers=list(data.modifiers))


def map_noun_phrases(data) -> NounPhrases:
    return NounPhrases(noun_phrases=[map_noun_phrase(np) for np in data.noun_phrases])
