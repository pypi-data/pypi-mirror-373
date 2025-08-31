from enum import StrEnum, auto


class JitterStrategyType(StrEnum):
    none = auto()
    full = auto()
    equal = auto()
    decorrelated = auto()
