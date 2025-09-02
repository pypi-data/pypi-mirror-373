from typing import Any

from runtime.reflection.lite.core.objects.member import Member
from runtime.reflection.lite.core.objects.member_type import MemberType

class Variable(Member):
    __slots__ = [ "__variable_type" ]

    def __init__(
        self,
        variable_type: type[Any] | None
    ):
        super().__init__(MemberType.VARIABLE)
        self.__variable_type = variable_type

    @property
    def variable_type(self) -> type[Any] | None:
        """The variables annotated or inferred type.
        """
        return self.__variable_type
