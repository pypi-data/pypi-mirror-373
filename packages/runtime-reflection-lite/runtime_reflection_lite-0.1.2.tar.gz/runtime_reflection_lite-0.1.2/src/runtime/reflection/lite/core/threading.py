from typing import Protocol
from types import TracebackType
from threading import RLock

class LockProtocol(Protocol): # pragma no cover
    def __enter__(self) -> None:
        ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None):
        ...


Lock: type[LockProtocol] = RLock # pyright: ignore[reportAssignmentType]

try:
    from runtime.threading import Lock # pyright: ignore[reportUnusedImport, reportMissingImports, reportUnknownVariableType]
except ImportError:
    pass