from typing import Any
from types import FrameType
from sys import modules
from inspect import FrameInfo,  stack
from typingutils import resolve_annotation

from runtime.reflection.lite.core.attributes import MODULE, FILE

def resolve(
    annotation: str,
    globals: dict[str, Any] | None = None,
    builtins: dict[str, Any] | None = None,
    locals: dict[str, Any] | None = None
) -> Any:
    if annotation[0] in ("'", '"'):
        annotation = annotation[1:]
    if annotation[-1] in ("'", '"'):
        annotation = annotation[:-1]

    if globals: # pragma: no cover
        globals = { **globals , **(builtins or  __builtins__)}

        try:
            result = eval(annotation, globals, locals)
            return resolve_annotation(result)
        except:
            pass

    # fallback
    for frame in stack()[1:]: # pragma: no cover
        if frame.filename == __file__:
            continue

        globals = { **frame.frame.f_globals , **frame.frame.f_builtins}
        locals = frame.frame.f_locals

        try:
            result = eval(annotation, globals, locals)
            return resolve_annotation(result)
        except:
            pass

    raise Exception(f"Unable to resolve {annotation}") # pragma: no cover

def get_frame(
    obj: Any,
    stack: list[FrameInfo],
    parent: Any | None
) -> FrameType | None: # pragma: no cover
    module = None

    if hasattr(obj, MODULE):
        module = modules[getattr(obj, MODULE)]
    elif parent and hasattr(parent, MODULE):
        module = modules[getattr(parent, MODULE)]

    if module and hasattr(module, FILE):
        for frame in stack:
            if frame.filename == module.__file__:
                frame_locals = frame.frame.f_locals.values()
                if parent is not None and parent in frame_locals:
                    return frame.frame
                elif obj in frame_locals:
                    return frame.frame
