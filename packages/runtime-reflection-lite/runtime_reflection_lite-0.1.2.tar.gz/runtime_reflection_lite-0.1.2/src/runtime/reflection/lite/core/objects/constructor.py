from typing import Any

from runtime.reflection.lite.core.objects.signature import Signature
from runtime.reflection.lite.core.objects.method import Method
from runtime.reflection.lite.core.objects.function_kind import FunctionKind
from runtime.reflection.lite.core.objects.undefined import Undefined
from runtime.reflection.lite.core.objects.member_type import MemberType
from runtime.reflection.lite.core.types import FUNCTION_AND_METHOD_TYPES

class Constructor(Method):
    __slots__ = [ ]

    def __init__(
        self,
        bound_cls: type[Any],
        signature: Signature,
        reflected: FUNCTION_AND_METHOD_TYPES
    ):
        super().__init__(MemberType.METHOD, FunctionKind.CONSTRUCTOR, bound_cls, signature, False, reflected)

    @property
    def return_type(self) -> type[Any]:
        return Undefined