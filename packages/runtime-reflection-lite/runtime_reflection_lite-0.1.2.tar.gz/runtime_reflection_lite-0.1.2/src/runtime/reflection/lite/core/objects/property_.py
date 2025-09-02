from typing import Any

from runtime.reflection.lite.core.objects.signature import Signature
from runtime.reflection.lite.core.objects.member import Member
from runtime.reflection.lite.core.objects.member_type import MemberType

class Property(Member):
    __slots__ = [ "__getter", "__setter", "__deleter", "__abstract", "__bound_cls", "__reflected" ]

    def __init__(
        self,
        bound_cls: type[Any],
        getter: Signature,
        setter: Signature | None,
        deleter: Signature | None,
        abstract: bool,
        reflected: property
    ):
        super().__init__(MemberType.PROPERTY)
        self.__getter = getter
        self.__setter = setter
        self.__deleter = deleter
        self.__abstract = abstract
        self.__bound_cls = bound_cls
        self.__reflected = reflected

    @property
    def bound_cls(self) -> type[Any]:
        """The property's bound class.
        """
        return self.__bound_cls

    @property
    def property_type(self) -> type[Any]:
        """The property type.
        """
        return self.__getter.return_type

    @property
    def getter(self) -> Signature:
        """The signature of the property getter.
        """
        return self.__getter

    @property
    def setter(self) -> Signature | None:
        """The signature of the property setter (if any).
        """
        return self.__setter

    @property
    def deleter(self) -> Signature | None:
        """The signature of the property deleter (if any).
        """
        return self.__deleter

    @property
    def is_abstract(self) -> bool:
        """Indicates if property is abstract.
        """
        return self.__abstract

    @property
    def is_readonly(self) -> bool:
        """Indicates if property is readonly or not (i.e. has a setter).
        """
        return self.__setter is None

    @property
    def reflected(self) -> property:
        """The property reflected.
        """
        return self.__reflected