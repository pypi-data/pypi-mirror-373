"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
from ..types import noun_phrase_pb2 as types_dot_noun__phrase__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18types/concept_type.proto\x12\x08protocol\x1a\x17types/noun_phrase.proto"B\n\x13ConceptOptionalType\x12+\n\x05inner\x18\x01 \x01(\x0b2\x15.protocol.ConceptTypeR\x05inner"C\n\x14ConceptSensitiveType\x12+\n\x05inner\x18\x01 \x01(\x0b2\x15.protocol.ConceptTypeR\x05inner">\n\x0fConceptListType\x12+\n\x05inner\x18\x01 \x01(\x0b2\x15.protocol.ConceptTypeR\x05inner"A\n\x10ConceptUnionType\x12-\n\x06inners\x18\x01 \x03(\x0b2\x15.protocol.ConceptTypeR\x06inners"\xb5\x01\n\x15ConceptDictionaryType\x12\'\n\x04is_a\x18\x01 \x03(\x0b2\x14.protocol.NounPhraseR\x03isA\x12<\n\x06fields\x18\x02 \x03(\x0b2$.protocol.ConceptDictionaryTypeFieldR\x06fields\x12%\n\x0bdescription\x18\x03 \x01(\tH\x00R\x0bdescription\x88\x01\x01B\x0e\n\x0c_description"\x92\x01\n\x1aConceptDictionaryTypeField\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12+\n\x05value\x18\x02 \x01(\x0b2\x15.protocol.ConceptTypeR\x05value\x12%\n\x0bdescription\x18\x03 \x01(\tH\x00R\x0bdescription\x88\x01\x01B\x0e\n\x0c_description"\x85\x01\n\x10ConceptTableType\x12:\n\x07columns\x18\x01 \x03(\x0b2 .protocol.ConceptTableTypeColumnR\x07columns\x12%\n\x0bdescription\x18\x02 \x01(\tH\x00R\x0bdescription\x88\x01\x01B\x0e\n\x0c_description"\x8e\x01\n\x16ConceptTableTypeColumn\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12+\n\x05value\x18\x02 \x01(\x0b2\x15.protocol.ConceptTypeR\x05value\x12%\n\x0bdescription\x18\x03 \x01(\tH\x00R\x0bdescription\x88\x01\x01B\x0e\n\x0c_description"s\n\x11ConceptOpaqueType\x12\'\n\x04is_a\x18\x01 \x03(\x0b2\x14.protocol.NounPhraseR\x03isA\x12%\n\x0bdescription\x18\x02 \x01(\tH\x00R\x0bdescription\x88\x01\x01B\x0e\n\x0c_description"\x10\n\x0eConceptAnyType"\x11\n\x0fConceptSelfType"\x99\x01\n\x15ConceptEnumTypeMember\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\x125\n\x0bnoun_phrase\x18\x02 \x01(\x0b2\x14.protocol.NounPhraseR\nnounPhrase\x12%\n\x0bdescription\x18\x03 \x01(\tH\x00R\x0bdescription\x88\x01\x01B\x0e\n\x0c_description"\xac\x01\n\x0fConceptEnumType\x12\'\n\x04is_a\x18\x01 \x03(\x0b2\x14.protocol.NounPhraseR\x03isA\x129\n\x07members\x18\x02 \x03(\x0b2\x1f.protocol.ConceptEnumTypeMemberR\x07members\x12%\n\x0bdescription\x18\x03 \x01(\tH\x00R\x0bdescription\x88\x01\x01B\x0e\n\x0c_description"\xe5\x05\n\x0bConceptType\x12>\n\x0bscalar_type\x18\x01 \x01(\x0e2\x1b.protocol.ConceptScalarTypeH\x00R\nscalarType\x12D\n\roptional_type\x18\x02 \x01(\x0b2\x1d.protocol.ConceptOptionalTypeH\x00R\x0coptionalType\x128\n\tlist_type\x18\x03 \x01(\x0b2\x19.protocol.ConceptListTypeH\x00R\x08listType\x12J\n\x0fdictionary_type\x18\x04 \x01(\x0b2\x1f.protocol.ConceptDictionaryTypeH\x00R\x0edictionaryType\x12;\n\ntable_type\x18\x05 \x01(\x0b2\x1a.protocol.ConceptTableTypeH\x00R\ttableType\x12>\n\x0bopaque_type\x18\x06 \x01(\x0b2\x1b.protocol.ConceptOpaqueTypeH\x00R\nopaqueType\x125\n\x08any_type\x18\x07 \x01(\x0b2\x18.protocol.ConceptAnyTypeH\x00R\x07anyType\x12;\n\nunion_type\x18\x08 \x01(\x0b2\x1a.protocol.ConceptUnionTypeH\x00R\tunionType\x128\n\tself_type\x18\t \x01(\x0b2\x19.protocol.ConceptSelfTypeH\x00R\x08selfType\x12G\n\x0esensitive_type\x18\n \x01(\x0b2\x1e.protocol.ConceptSensitiveTypeH\x00R\rsensitiveType\x128\n\tenum_type\x18\x0b \x01(\x0b2\x19.protocol.ConceptEnumTypeH\x00R\x08enumTypeB\x1c\n\x1aconcept_type_discriminator*\x95\x02\n\x11ConceptScalarType\x12\x1f\n\x1bConceptScalarTypeConceptual\x10\x00\x12\x19\n\x15ConceptScalarTypeText\x10\x01\x12\x1b\n\x17ConceptScalarTypeNumber\x10\x02\x12\x1c\n\x18ConceptScalarTypeBoolean\x10\x03\x12\x1d\n\x19ConceptScalarTypeDatetime\x10\x04\x12\x19\n\x15ConceptScalarTypeDate\x10\x05\x12\x19\n\x15ConceptScalarTypeTime\x10\x06\x12\x19\n\x15ConceptScalarTypeFile\x10\x07\x12\x19\n\x15ConceptScalarTypeUUID\x10\x08B\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'types.concept_type_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_CONCEPTSCALARTYPE']._serialized_start = 2175
    _globals['_CONCEPTSCALARTYPE']._serialized_end = 2452
    _globals['_CONCEPTOPTIONALTYPE']._serialized_start = 63
    _globals['_CONCEPTOPTIONALTYPE']._serialized_end = 129
    _globals['_CONCEPTSENSITIVETYPE']._serialized_start = 131
    _globals['_CONCEPTSENSITIVETYPE']._serialized_end = 198
    _globals['_CONCEPTLISTTYPE']._serialized_start = 200
    _globals['_CONCEPTLISTTYPE']._serialized_end = 262
    _globals['_CONCEPTUNIONTYPE']._serialized_start = 264
    _globals['_CONCEPTUNIONTYPE']._serialized_end = 329
    _globals['_CONCEPTDICTIONARYTYPE']._serialized_start = 332
    _globals['_CONCEPTDICTIONARYTYPE']._serialized_end = 513
    _globals['_CONCEPTDICTIONARYTYPEFIELD']._serialized_start = 516
    _globals['_CONCEPTDICTIONARYTYPEFIELD']._serialized_end = 662
    _globals['_CONCEPTTABLETYPE']._serialized_start = 665
    _globals['_CONCEPTTABLETYPE']._serialized_end = 798
    _globals['_CONCEPTTABLETYPECOLUMN']._serialized_start = 801
    _globals['_CONCEPTTABLETYPECOLUMN']._serialized_end = 943
    _globals['_CONCEPTOPAQUETYPE']._serialized_start = 945
    _globals['_CONCEPTOPAQUETYPE']._serialized_end = 1060
    _globals['_CONCEPTANYTYPE']._serialized_start = 1062
    _globals['_CONCEPTANYTYPE']._serialized_end = 1078
    _globals['_CONCEPTSELFTYPE']._serialized_start = 1080
    _globals['_CONCEPTSELFTYPE']._serialized_end = 1097
    _globals['_CONCEPTENUMTYPEMEMBER']._serialized_start = 1100
    _globals['_CONCEPTENUMTYPEMEMBER']._serialized_end = 1253
    _globals['_CONCEPTENUMTYPE']._serialized_start = 1256
    _globals['_CONCEPTENUMTYPE']._serialized_end = 1428
    _globals['_CONCEPTTYPE']._serialized_start = 1431
    _globals['_CONCEPTTYPE']._serialized_end = 2172