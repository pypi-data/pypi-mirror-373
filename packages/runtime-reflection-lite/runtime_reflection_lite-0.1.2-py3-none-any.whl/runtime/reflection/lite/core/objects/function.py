from typing import Any
from weakref import ref, ReferenceType

from runtime.reflection.lite.core.objects.signature import Signature
from runtime.reflection.lite.core.objects.function_kind import FunctionKind
from runtime.reflection.lite.core.objects.member import Member
from runtime.reflection.lite.core.objects.member_type import MemberType
from runtime.reflection.lite.core.types import FUNCTION_AND_METHOD_TYPES



class Function(Member):
    __slots__ = [ "__kind", "__signature", "__reflected" ]

    def __init__(
        self,
        member_type: MemberType,
        kind: FunctionKind,
        signature: Signature,
        reflected: FUNCTION_AND_METHOD_TYPES
    ):
        super().__init__(member_type)
        self.__kind = kind
        self.__signature = signature
        self.__reflected = ref(reflected)

    @property
    def kind(self) -> FunctionKind:
        """The function kind.
        """
        return self.__kind

    @property
    def return_type(self) -> type[Any]:
        """The function return type.
        """
        return self.__signature.return_type

    @property
    def signature(self) -> Signature:
        """The function signature.
        """
        return self.__signature

    @property
    def reflected(self) -> ReferenceType[FUNCTION_AND_METHOD_TYPES]:
        """The function reflected (weak reference).
        """
        return self.__reflected