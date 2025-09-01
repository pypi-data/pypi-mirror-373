from enum import Enum


class DependencyManagerType(Enum):
    UNKNOWN = 0
    PIP = 1
    POETRY = 2
    CONDA = 3
