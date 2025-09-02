from enum import Enum

class MemberType(Enum):
    CLASS = 1
    FIELD = 2
    VARIABLE = 3
    DELEGATE = 4
    PROPERTY = 5
    FUNCTION = 6
    METHOD = 7
    MODULE = 8