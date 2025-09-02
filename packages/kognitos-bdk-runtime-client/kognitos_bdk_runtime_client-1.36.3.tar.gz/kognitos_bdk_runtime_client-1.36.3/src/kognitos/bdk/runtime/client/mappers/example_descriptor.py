# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.example_descriptor import ExampleDescriptor
from kognitos.bdk.runtime.client.proto.types.example_descriptor_pb2 import \
    ExampleDescriptor as ProtoExampleDescriptor


def map_example_descriptor(data: ProtoExampleDescriptor) -> ExampleDescriptor:
    return ExampleDescriptor(description=data.description, snippet=data.snippet)
