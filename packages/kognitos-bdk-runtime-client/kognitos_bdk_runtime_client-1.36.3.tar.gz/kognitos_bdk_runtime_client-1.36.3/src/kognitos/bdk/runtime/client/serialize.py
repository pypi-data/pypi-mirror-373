import base64
import json
from builtins import bool, bytes, dict, float, int, list, str
from datetime import date, datetime, time
from enum import Enum
from typing import Any, List, Optional, Type

# NOTE: The following list of imports are here so that they're available in the global scope and we're
# able to serialize/deserialize them properly.
# pylint: disable=unused-import
from kognitos.bdk.runtime.client.book_authentication_descriptor import (
    BookAuthenticationDescriptor, BookCustomAuthenticationDescriptor,
    BookOAuthAuthenticationDescriptor, OauthArgumentDescriptor, OauthFlow,
    OauthProvider)
from kognitos.bdk.runtime.client.book_descriptor import BookDescriptor
from kognitos.bdk.runtime.client.book_procedure_descriptor import \
    BookProcedureDescriptor
from kognitos.bdk.runtime.client.book_procedure_signature import \
    BookProcedureSignature
from kognitos.bdk.runtime.client.concept_descriptor import ConceptDescriptor
from kognitos.bdk.runtime.client.concept_type import (
    ConceptAnyType, ConceptDictionaryType, ConceptDictionaryTypeField,
    ConceptEnumType, ConceptEnumTypeMember, ConceptListType, ConceptOpaqueType,
    ConceptOptionalType, ConceptScalarType, ConceptSelfType,
    ConceptSensitiveType, ConceptTableType, ConceptTableTypeColumn,
    ConceptUnionType)
from kognitos.bdk.runtime.client.concept_value import ConceptValue
from kognitos.bdk.runtime.client.connection_required import ConnectionRequired
from kognitos.bdk.runtime.client.credential_descriptor import (
    CredentialDescriptor, CredentialType)
from kognitos.bdk.runtime.client.environment_information import \
    EnvironmentInformation
from kognitos.bdk.runtime.client.example_descriptor import ExampleDescriptor
from kognitos.bdk.runtime.client.expression import (BinaryExpression,
                                                    BinaryOperator,
                                                    UnaryExpression)
from kognitos.bdk.runtime.client.input_concept import InputConcept
from kognitos.bdk.runtime.client.noun_phrase import NounPhrase, NounPhrases
from kognitos.bdk.runtime.client.promise import Promise
from kognitos.bdk.runtime.client.question_answer import (AnsweredQuestion,
                                                         Question)
from kognitos.bdk.runtime.client.question_descriptor import QuestionDescriptor
from kognitos.bdk.runtime.client.sensitive import Sensitive
from kognitos.bdk.runtime.client.test_connection import TestConnectionResponse
from kognitos.bdk.runtime.client.value import (BooleanValue, ConceptualValue,
                                               DatetimeValue, DateValue,
                                               DictionaryValue, File,
                                               ListValue, NullValue,
                                               NumberValue, OpaqueValue,
                                               RemoteFile, TextValue,
                                               TimeValue)

# pylint: enable=unused-import


class BDKSerializableNone:
    """Python 3.9 doesn't have NoneType withi `typing`, so we need to create our own for serialization's sake"""


def to_bytes(obj: Any) -> bytes:
    """
    Creates a representation of the object as a dictionary of

    key: [type, serialized_value]
    """

    def to_dict(obj):
        if isinstance(obj, (str, int, float, bool, bytes)):
            if isinstance(obj, bytes):
                return (obj.__class__.__name__, obj.decode("utf-8"))
            return (obj.__class__.__name__, obj)

        if hasattr(obj, "__dataclass_fields__"):
            as_dict = obj.__dict__
            return (obj.__class__.__name__, {k: to_dict(v) for k, v in as_dict.items()})

        if isinstance(obj, dict):
            return (obj.__class__.__name__, {k: to_dict(v) for k, v in obj.items()})

        if isinstance(obj, list):
            return (obj.__class__.__name__, [to_dict(v) for v in obj])

        if isinstance(obj, Enum):
            return (obj.__class__.__name__, obj.value)

        if obj is None:
            return ("BDKSerializableNone", None)

        if isinstance(obj, (date, datetime, time)):
            return (obj.__class__.__name__, obj.isoformat())

        raise ValueError(f"Unsupported type: {type(obj)}")

    return bytes(json.dumps(to_dict(obj)), "utf-8")


def from_bytes(obj: bytes, additional_types: Optional[List[Type]] = None) -> Any:
    as_dict = json.loads(obj.decode("utf-8"))
    additional_types_map = (
        {t.__name__: t for t in additional_types} if additional_types else {}
    )

    def from_dict(as_dict):
        type_name, value = as_dict

        is_valid_type = type_name in globals() or type_name in additional_types_map

        if not is_valid_type:
            raise ValueError(f"Unsupported type: {type_name}")

        cls = globals().get(type_name) or additional_types_map.get(type_name)

        if not cls:
            raise ValueError(f"Unsupported type: {type_name}")

        if cls in (str, int, float, bool):
            return cls(value)

        if cls == bytes:
            return bytes(value, "utf-8")

        if hasattr(cls, "__dataclass_fields__"):
            return cls(**{k: from_dict(v) for k, v in value.items()})

        if cls == dict:
            return cls({k: from_dict(v) for k, v in value.items()})

        if cls == list:
            return [from_dict(v) for v in value]

        if issubclass(cls, Enum):
            return cls(value)

        if cls == BDKSerializableNone:
            return None

        if cls == date:
            return date.fromisoformat(value)

        if cls == datetime:
            return datetime.fromisoformat(value)

        if cls == time:
            return time.fromisoformat(value)

        raise ValueError(f"Unsupported type: {type(obj)}")

    return from_dict(as_dict)


def compute_hash(obj: Any) -> bytes:
    return base64.b64encode(to_bytes(obj))
