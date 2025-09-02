from __future__ import annotations
from typing import Any

from runtime.reflection.lite.core.objects.field import Member
from runtime.reflection.lite.core.objects.member_type import MemberType

class Delegate(Member):
    __slots__ = ["__delegate_type", "__parent_cls", "__reflected"]
    def __init__(
        self,
        delegate_type: type,
        parent_cls: type[Any],
        reflected: Any
    ):
        super().__init__(MemberType.DELEGATE)
        self.__delegate_type = delegate_type
        self.__parent_cls = parent_cls
        self.__reflected = reflected


    @property
    def delegate_type(self) -> type:
        """The delegate's type
        """
        return self.__delegate_type

    @property
    def parent_cls(self) -> type[Any]:
        """The class on which the delegate is defined.
        """
        return self.__parent_cls

    @property
    def reflected(self) -> Any:
        """The delegate instance
        """
        return self.__reflected

