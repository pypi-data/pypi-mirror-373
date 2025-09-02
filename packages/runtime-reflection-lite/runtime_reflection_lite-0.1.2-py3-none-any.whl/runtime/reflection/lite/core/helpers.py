from typing import Any, cast
from types import FrameType, ModuleType
from typingutils import AnyFunction
from deprecated import deprecated

from runtime.reflection.lite.core.objects.signature import Signature
from runtime.reflection.lite.core.attributes import INIT
from runtime.reflection.lite.core import get_signature

@deprecated("Use get_signature() instead", version = "0.1.0")
def reflect_function(
    fn: AnyFunction,
    cls: object | None = None
) -> Signature: # pragma: no cover
    """Gets the signature of the specified function.

    Args:
        fn (AnyFunction): The function on which to reflect.
        cls (object | None, optional): The class to which the function belongs (if any). Defaults to None.

    Returns:
        Signature: Returns a function signature.
    """
    return get_signature(fn, cast(type[Any] | FrameType | ModuleType, cls))

def get_constructor(cls: type[Any]) -> Signature: # pragma: no cover
    """Gets the signature of the specified class' constructor. Note that overloads aren't taken into account.

    Args:
        cls (type[Any]): The class reflected.

    Returns:
        Signature: Returns a function signature.
    """
    return get_signature(getattr(cls, INIT), cls)