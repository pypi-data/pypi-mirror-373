from typing import Any
from types import ModuleType, FrameType
from typingutils import is_type

from runtime.reflection.lite.core.objects.access_mode import AccessMode
from runtime.reflection.lite.core.attributes import ANNOTATIONS, GET
from runtime.reflection.lite.core.types import FUNCTION_TYPES, METHOD_TYPES


def is_special_attribute(attr: str) -> bool:
    return attr.startswith("__") and attr.endswith("__")

def is_protected_attribute(attr: str) -> bool:
    return attr.startswith("_") and not attr.startswith("__")

def is_private_attribute(attr: str) -> bool:
    return attr.startswith("__") and not attr.endswith("__")

def is_delegate(value: Any) -> bool:
    if hasattr(value, GET) and ( attr_get := getattr(value, GET) ):
        if isinstance(attr_get, (FUNCTION_TYPES, METHOD_TYPES)):
            from runtime.reflection.lite.core import get_signature
            sig = get_signature(attr_get)
            if len(sig.parameters) == 2:
                if sig.parameters[1].parameter_type and is_type(sig.parameters[1].parameter_type):
                    return  True
                elif not sig.parameters[0].parameter_type and not sig.parameters[1].parameter_type and sig.parameters[0].name == "instance" and sig.parameters[1].name == "owner":
                    return True
                else:
                    pass # pragma: no cover
            else:
                pass # pragma: no cover

    return False

def get_access_mode(parent: type | ModuleType | FrameType | None, name: str) -> tuple[str, AccessMode]:
    if parent and isinstance(parent, (type, ModuleType)) and name.startswith(f"_{parent.__name__}__"):
        return name[len(parent.__name__)+1:], AccessMode.PRIVATE
    elif is_private_attribute(name):
        return name, AccessMode.PRIVATE # pragma: no cover
    elif is_protected_attribute(name):
        return name, AccessMode.PROTECTED
    else:
        return name, AccessMode.PUBLIC

# def get_qualified_name(obj: Any) -> str:
#     if hasattr(obj, QUALIFIED_NAME):
#         return getattr(obj, QUALIFIED_NAME)
#     else:
#         return get_name(obj)

# def get_name(obj: Any) -> str:
#     if obj is None:
#         raise ValueError("Unable to get name of None")

#     if is_type(obj):
#         if is_generic_type(obj):
#             if not hasattr(obj, "_name") or not getattr(obj, "_name"):
#                 obj = get_generic_origin(obj)
#             if hasattr(obj, "_name"):
#                 return getattr(obj, "_name")

#     elif isinstance(obj, property):
#         return get_name(obj.fget)
#     elif isinstance(obj, (FrameType, FrameInfo)):
#         return "<Frame>"

#     if hasattr(obj, NAME):
#         return obj.__name__
#     else:
#         raise Exception("Unable to get object name" + str(obj))

def get_annotations(obj: Any) -> dict[str, str | type]:
    if hasattr(obj, ANNOTATIONS) and ( annotations := getattr(obj, ANNOTATIONS)):
        return annotations
        # return {
        #     name: getattr(value, ORIGIN) if isinstance(value, Annotated) else value
        #     for name, value in annotations.items()
        # }
    return {}