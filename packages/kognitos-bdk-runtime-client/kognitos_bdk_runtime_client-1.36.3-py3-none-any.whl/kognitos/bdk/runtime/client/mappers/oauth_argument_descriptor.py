from kognitos.bdk.runtime.client.book_authentication_descriptor import \
    OauthArgumentDescriptor
# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.types.oauth_argument_descriptor_pb2 import \
    OAuthArgumentDescriptor as ProtoOAuthArgumentDescriptor

# pylint: enable=no-name-in-module


def map_oauth_argument_descriptor(
    data: ProtoOAuthArgumentDescriptor,
) -> OauthArgumentDescriptor:
    return OauthArgumentDescriptor(
        id=data.id,
        name=data.name,
        description=data.description,
    )
