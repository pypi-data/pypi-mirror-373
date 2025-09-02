from typing import Any
from types import ModuleType, FrameType
from runtime.reflection.lite.core.objects.member import Member
from runtime.reflection.lite.core.objects.member_type import MemberType
from runtime.reflection.lite.core.objects.access_mode import AccessMode
from runtime.reflection.lite.core.misc import is_special_attribute

class MemberInfo:
    __slots__ = [ "__name", "__org_name", "__type", "__class", "__access_mode", "__is_special", "__is_inherited", "__parent"]

    def __init__(
        self,
        name: str,
        org_name: str,
        member_class: type,
        member_type: MemberType,
        access_mode: AccessMode,
        is_inherited: bool,
        parent: type[Any] | ModuleType | FrameType,
    ):
        self.__name = name
        self.__org_name = org_name
        self.__type = member_type
        self.__class = member_class
        self.__access_mode = access_mode
        self.__is_inherited = is_inherited
        self.__is_special = is_special_attribute(name)
        self.__parent = parent

    @property
    def name(self) -> str:
        """The member name.
        """
        return self.__name

    @property
    def org_name(self) -> str:
        """The original member name (names of private class members are mangled by prefixing the class name).
        """
        return self.__org_name

    @property
    def member_class(self) -> type[Member]:
        """The member class.
        """
        return self.__class

    @property
    def member_type(self) -> MemberType:
        """The member type.
        """
        return self.__type

    @property
    def access_mode(self) -> AccessMode:
        """The member access mode (or encapsulation).
        """
        return self.__access_mode

    @property
    def is_inherited(self) -> bool:
        """Indicates whether or not member is inherited from a base class.
        """
        return self.__is_inherited

    @property
    def is_special(self) -> bool:
        """Indicates whether or not member is a special pythonic member (i.e. it's name starts and ends with a double underscore).
        """
        return self.__is_special

    @property
    def parent(self) -> type[Any] | ModuleType | FrameType:
        """The object that defines the member.
        """
        return self.__parent

