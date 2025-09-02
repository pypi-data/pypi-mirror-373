# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.types.concept_type_pb2 import \
    ConceptType as ProtoConceptType

from ..concept_type import (ConceptAnyType, ConceptDictionaryType,
                            ConceptDictionaryTypeField, ConceptEnumType,
                            ConceptEnumTypeMember, ConceptListType,
                            ConceptOpaqueType, ConceptOptionalType,
                            ConceptScalarType, ConceptSelfType,
                            ConceptSensitiveType, ConceptTableType,
                            ConceptTableTypeColumn, ConceptType,
                            ConceptUnionType)
from . import noun_phrase as np


def map_concept_type(data: ProtoConceptType) -> ConceptType:
    concept_type = data.WhichOneof("concept_type_discriminator")

    if concept_type == "scalar_type":
        return ConceptScalarType(data.scalar_type)

    if concept_type == "optional_type":
        return ConceptOptionalType(inner=map_concept_type(data.optional_type.inner))

    if concept_type == "sensitive_type":
        return ConceptSensitiveType(inner=map_concept_type(data.sensitive_type.inner))

    if concept_type == "any_type":
        return ConceptAnyType()

    if concept_type == "self_type":
        return ConceptSelfType()

    if concept_type == "dictionary_type":
        return ConceptDictionaryType(
            is_a=[np.map_noun_phrase(is_a) for is_a in data.dictionary_type.is_a],
            fields=[
                ConceptDictionaryTypeField(
                    key=f.key,
                    value=map_concept_type(f.value),
                    description=f.description,
                )
                for f in data.dictionary_type.fields
            ],
            description=data.dictionary_type.description,
        )

    if concept_type == "list_type":
        return ConceptListType(inner=map_concept_type(data.list_type.inner))

    if concept_type == "table_type":
        return ConceptTableType(
            columns=[
                ConceptTableTypeColumn(key=h.key, value=map_concept_type(h.value))
                for h in data.table_type.columns
            ],
            description=data.table_type.description,
        )

    if concept_type == "union_type":
        return ConceptUnionType(
            inners=[map_concept_type(t) for t in data.union_type.inners]
        )

    if concept_type == "opaque_type":
        return ConceptOpaqueType(
            is_a=[np.map_noun_phrase(is_a) for is_a in data.opaque_type.is_a],
            description=data.opaque_type.description,
        )

    if concept_type == "enum_type":
        return ConceptEnumType(
            is_a=[np.map_noun_phrase(is_a) for is_a in data.enum_type.is_a],
            members=[
                ConceptEnumTypeMember(
                    name=m.name,
                    noun_phrase=np.map_noun_phrase(m.noun_phrase),
                    description=m.description,
                )
                for m in data.enum_type.members
            ],
            description=data.enum_type.description,
        )

    raise ValueError(f"Concept Type of type '{concept_type}'")
