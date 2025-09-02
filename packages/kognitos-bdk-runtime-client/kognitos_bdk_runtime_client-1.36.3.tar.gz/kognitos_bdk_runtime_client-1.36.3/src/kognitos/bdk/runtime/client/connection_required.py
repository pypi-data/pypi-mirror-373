from enum import Enum


class ConnectionRequired(Enum):
    OPTIONAL = 0
    ALWAYS = 1
    NEVER = 2
