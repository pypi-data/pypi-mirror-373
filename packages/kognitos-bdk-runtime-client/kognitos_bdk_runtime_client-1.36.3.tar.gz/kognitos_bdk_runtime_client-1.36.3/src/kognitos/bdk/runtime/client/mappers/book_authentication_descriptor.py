from kognitos.bdk.runtime.client.book_authentication_descriptor import (
    BookAuthenticationDescriptor, BookCustomAuthenticationDescriptor,
    BookOAuthAuthenticationDescriptor, OauthFlow, OauthProvider)
# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.mappers.noun_phrase import map_noun_phrase
from kognitos.bdk.runtime.client.proto.types.book_authentication_descriptor_pb2 import \
    BookAuthenticationDescriptor as ProtoBookAuthenticationDescriptor

from . import credential_descriptor, oauth_argument_descriptor


def map_book_authentication_descriptor(
    data: ProtoBookAuthenticationDescriptor,
) -> BookAuthenticationDescriptor:
    auth_type = data.WhichOneof("authentication_discriminator")

    if auth_type == "oauth":
        auth = data.oauth
        return BookOAuthAuthenticationDescriptor(
            id=auth.id,
            provider=OauthProvider(auth.provider),
            flows=[OauthFlow(f) for f in auth.flows],
            authorize_endpoint=auth.authorize_endpoint,
            token_endpoint=auth.token_endpoint,
            scope=auth.scope,  # type: ignore
            name=auth.name or "oauth",
            arguments=[
                oauth_argument_descriptor.map_oauth_argument_descriptor(arg)
                for arg in auth.arguments
            ],
        )
    if auth_type == "custom":
        auth = data.custom
        return BookCustomAuthenticationDescriptor(
            id=auth.id,
            credentials=[
                credential_descriptor.map_credential_descriptor(cd)
                for cd in auth.credentials
            ],
            description=auth.description,
            name=auth.name or auth.id,
            noun_phrase=map_noun_phrase(auth.noun_phrase),
        )

    raise ValueError(f"Cannot map authentication of type {auth_type}")
