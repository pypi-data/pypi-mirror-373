from enum import Enum, auto


class ConfigStep(Enum):
    DATABASE = auto()
    SETTINGS = auto()
    ALL = auto()
