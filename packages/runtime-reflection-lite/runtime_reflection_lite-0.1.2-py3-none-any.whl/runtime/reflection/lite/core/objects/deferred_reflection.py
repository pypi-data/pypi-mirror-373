from typing import Protocol, TypeVar, runtime_checkable

from runtime.reflection.lite.core.objects.member import Member

T = TypeVar("T", bound = Member, covariant = True)

@runtime_checkable
class DeferredReflection(Protocol[T]): # pragma: no cover

    def __call__(self) -> T:
        ...