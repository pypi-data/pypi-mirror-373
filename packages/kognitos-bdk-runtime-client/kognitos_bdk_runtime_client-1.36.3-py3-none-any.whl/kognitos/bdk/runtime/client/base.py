import pprint
from dataclasses import dataclass


@dataclass
class BdkDescriptorBase:
    def __post_init__(self):
        """
        Checks all inner fields and forces then to be an actual python list
        if their type hint is `List[Any]`. This helps us on serialization issues we may have
        downstream.
        """
        fields = self.__dataclass_fields__  # pylint: disable=no-member
        for field_name, field_info in fields.items():
            try:
                if field_info.type._name == "List":
                    setattr(self, field_name, list(getattr(self, field_name)))
            except AttributeError:
                pass

    def __str__(self):
        return pprint.pformat(self)
