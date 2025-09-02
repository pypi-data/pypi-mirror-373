from kognitos.bdk.runtime.client.credential_descriptor import (
    CredentialDescriptor, CredentialType)


def map_credential_descriptor(data) -> CredentialDescriptor:
    return CredentialDescriptor(
        id=data.id,
        type=CredentialType(data.type),
        label=data.label,
        visible=data.visible,
        description=data.description,
    )
