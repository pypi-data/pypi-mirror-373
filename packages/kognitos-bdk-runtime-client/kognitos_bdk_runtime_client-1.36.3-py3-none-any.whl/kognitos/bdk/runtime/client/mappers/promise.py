from kognitos.bdk.runtime.client.promise import Promise
from kognitos.bdk.runtime.client.proto.types.promise_pb2 import \
    Promise as ProtoPromise  # pylint: disable=no-name-in-module

from . import value as value_mapper


def map_promise(promise: ProtoPromise) -> Promise:
    return Promise(
        promise_resolver_function_name=promise.promise_resolver_function_name,
        data=value_mapper.map_value(promise.data),
    )
