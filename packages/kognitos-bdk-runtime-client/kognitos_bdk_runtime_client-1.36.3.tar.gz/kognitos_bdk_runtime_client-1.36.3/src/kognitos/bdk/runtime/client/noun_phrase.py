import re
from dataclasses import dataclass
from typing import List, Optional

from .base import BdkDescriptorBase


@dataclass
class NounPhrase(BdkDescriptorBase):
    head: str
    modifiers: Optional[List[str]] = None

    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = []

        super().__post_init__()

    def __str__(self) -> str:
        modifiers = self.modifiers or []
        return " ".join(modifiers + [self.head])

    def __hash__(self) -> int:
        return hash(str(self))

    @staticmethod
    def from_str(s: str):
        """
        Creates a NounPhrase from a string. The string must be in the format
        <modifier1> <modifier2> ... <head>
        """
        *modifiers, head = s.split(" ")
        return NounPhrase(head=head, modifiers=modifiers)

    @classmethod
    def from_snake_case(cls, snake_str: str) -> "NounPhrase":
        """
        Creates a NounPhrase from a snake_case string.
        """
        # replace underscores with spaces
        words = snake_str.replace("_", " ")
        return NounPhrase(head=words, modifiers=[])

    @classmethod
    def from_pascal_case(cls, pascal_str: str) -> "NounPhrase":
        """
        Creates a NounPhrase from a pascal_case string.
        """
        # remove existing spaces
        pascal_str = pascal_str.replace(" ", "")
        # insert space before each capital letter (except the first one)
        words = re.sub(
            r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", pascal_str
        ).lower()
        return NounPhrase(head=words, modifiers=[])

    def to_camel_case(self) -> str:
        """
        Converts the NounPhrase to camelCase.
        """
        snake_str = self.to_snake_case()
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    def to_snake_case(self) -> str:
        """
        Converts the NounPhrase to snake_case.
        """
        text = str(self)
        return text.lower().replace(" ", "_")

    def to_kebab_case(self) -> str:
        """
        Converts the NounPhrase to kebab-case.
        """
        snake_str = self.to_snake_case()
        return snake_str.replace("_", "-")


@dataclass
class NounPhrases(BdkDescriptorBase):
    noun_phrases: List[NounPhrase]

    def __str__(self) -> str:
        return "'s ".join([str(noun_phrase) for noun_phrase in self.noun_phrases])

    def __hash__(self) -> int:
        return hash(str(self))

    @staticmethod
    def from_str(s: str):
        """
        Creates a NounPhrases from a string. The string must be in the format
        <modifier1> <modifier2> ... <head>'s <modifier1> <modifier2> ... <head>'s ...
        """
        noun_phrases = []
        for np in s.split("'s"):
            if np:
                noun_phrases.append(NounPhrase.from_str(np))
        return NounPhrases(noun_phrases=noun_phrases)
