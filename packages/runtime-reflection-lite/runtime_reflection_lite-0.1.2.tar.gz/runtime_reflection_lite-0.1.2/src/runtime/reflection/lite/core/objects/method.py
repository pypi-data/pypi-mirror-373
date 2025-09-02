from typing import Any

from runtime.reflection.lite.core.objects.signature import Signature
from runtime.reflection.lite.core.objects.function import Function
from runtime.reflection.lite.core.objects.function_kind import FunctionKind
from runtime.reflection.lite.core.objects.member_type import MemberType
from runtime.reflection.lite.core.types import FUNCTION_AND_METHOD_TYPES

class Method(Function):
    __slots__ = [ "__abstract", "__bound_cls" ]

    def __init__(
        self,
        member_type: MemberType,
        kind: FunctionKind,
        bound_cls: type[Any],
        signature: Signature,
        abstract: bool,
        reflected: FUNCTION_AND_METHOD_TYPES
    ):
        super().__init__(member_type, kind, signature, reflected)
        self.__abstract = abstract
        self.__bound_cls = bound_cls

    @property
    def bound_cls(self) -> type[Any]:
        """The methods bound class.
        """
        return self.__bound_cls

    @property
    def is_abstract(self) -> bool:
        """Indicates if method is abstract.
        """
        return self.__abstract
