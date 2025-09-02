from enum import Enum

class FunctionKind(Enum):
    FUNCTION = 1
    CLASS_METHOD = 2
    STATIC_METHOD = 3
    METHOD = 4
    CONSTRUCTOR = 5