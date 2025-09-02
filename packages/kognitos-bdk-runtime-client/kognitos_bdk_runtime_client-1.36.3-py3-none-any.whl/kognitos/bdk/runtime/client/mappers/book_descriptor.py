# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.types.book_descriptor_pb2 import \
    BookDescriptor as ProtoBookDescriptor

from ..book_descriptor import BookDescriptor
from ..noun_phrase import NounPhrase
from . import book_authentication_descriptor as bad
from . import concept_descriptor as cd


def format_name_as_display_name(name: str) -> str:
    # NOTE: This is a temporary fix to ensure that the display name is formatted correctly.
    # We may need to keep this for older books, so we don't break compatibility.
    # We need to enhance this upstreams anyways, and keep the logic in sync.
    if (
        name.lower() != name
    ):  # if the name has ANY capital letters, we assume it's already formatted correctly
        return name
    splitted_name = name.split(" ")
    capitalized_words = [word.capitalize() for word in splitted_name]
    return " ".join(capitalized_words)


def map_book_descriptor(data: ProtoBookDescriptor) -> BookDescriptor:
    noun_phrase = bad.map_noun_phrase(data.noun_phrase)
    if not str(noun_phrase):
        noun_phrase = NounPhrase(data.name)
    return BookDescriptor(
        id=data.id,
        name=data.name,
        short_description=data.short_description,
        long_description=data.long_description,
        author=data.author,
        icon=data.icon,
        version=data.version,
        authentications=[
            bad.map_book_authentication_descriptor(a) for a in data.authentications
        ],
        configurations=[cd.map_concept_descriptor(c) for c in data.configurations],
        display_name=format_name_as_display_name(data.display_name or data.name),
        endpoint=data.endpoint,
        # connection_required is optional in proto, so that we support older versions of the runtime
        # that don't have this field, so we default to False.
        connection_required=data.connection_required or False,
        tags=list(data.tags),
        # discover_capable is optional in proto, so that we support older versions of the runtime
        # that don't have this field, so we default to False.
        discover_capable=data.discover_capable or False,
        noun_phrase=noun_phrase,
    )
