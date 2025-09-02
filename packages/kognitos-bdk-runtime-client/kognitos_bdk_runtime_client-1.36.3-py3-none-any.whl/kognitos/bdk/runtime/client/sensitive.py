import builtins
from dataclasses import dataclass
from functools import wraps
from logging import Logger
from typing import Any, Set

from kognitos.bdk.runtime.client.proto.types.value_pb2 import \
    SensitiveValue as ProtoSensitiveValue  # pylint: disable=no-name-in-module

sensitive_data: Set[str] = set()


@dataclass
class Sensitive:
    def __init__(self, value: Any):
        sensitive_data.add(str(value))
        self.value = value

    def __str__(self):
        return "Sensitive(****)"

    def __repr__(self):
        return "Sensitive(****)"

    def __eq__(self, other):
        if isinstance(other, Sensitive):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(("Sensitive", self.value))


unwrapped_log_method = Logger._log
unwrapped_print_function = builtins.print


def scrub_filter(data: str):
    for sensitive in sorted(list(sensitive_data), reverse=True):
        data = data.replace(sensitive, "Sensitive(****)")
    return data


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@wraps(unwrapped_log_method)
def scrub_sensitive_data_from_logger(
    self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=2
):
    scrubbed_msg = scrub_filter(str(msg))
    return unwrapped_log_method(
        self,
        level,
        scrubbed_msg,
        args,
        exc_info=exc_info,
        extra=extra,
        stack_info=stack_info,
        stacklevel=stacklevel,
    )


@wraps(builtins.print)
def scrub_sensitive_data_from_print(*args, sep=" ", end="\n", file=None):
    scrubbed_args = (scrub_filter(str(arg)) for arg in args)
    return unwrapped_print_function(*scrubbed_args, sep=sep, end=end, file=file)


# NOTE: These will wrap the builtin print and the log function, so that there is no way around
#       to log any sensitive data, even if the source of the logging message does not come from
#       a Sensitive object in itself.

Logger._log = scrub_sensitive_data_from_logger
builtins.print = scrub_sensitive_data_from_print
print = scrub_sensitive_data_from_print  # pylint: disable=redefined-builtin

ProtoSensitiveValue.__str__ = wraps(ProtoSensitiveValue.__str__)(
    lambda _: "Sensitive(****)"
)
ProtoSensitiveValue.__repr__ = wraps(ProtoSensitiveValue.__repr__)(
    lambda _: "Sensitive(****)"
)
