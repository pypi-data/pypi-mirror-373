from runtime.reflection.lite.core.objects.member_type import MemberType

class Member:
    __slots__ = [ "__member_type", "__weakref__" ]

    def __init__(
        self,
        member_type: MemberType
    ):
        self.__member_type = member_type

    @property
    def member_type(self) -> MemberType:
        """The member type.
        """
        return self.__member_type
