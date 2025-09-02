from enum import Enum
from inspect import Parameter

class ParameterKind(Enum):
    """The ParameterKind class is an enumeration of the different kinds of parameters.
    """
    POSITIONAL = Parameter.POSITIONAL_ONLY
    KEYWORD = Parameter.KEYWORD_ONLY
    POSITIONAL_OR_KEYWORD = Parameter.POSITIONAL_OR_KEYWORD
    ARGS = Parameter.VAR_POSITIONAL
    KWARGS = Parameter.VAR_KEYWORD
