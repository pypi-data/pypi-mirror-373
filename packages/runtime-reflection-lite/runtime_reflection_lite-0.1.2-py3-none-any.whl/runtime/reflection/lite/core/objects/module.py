from __future__ import annotations
from types import ModuleType
from weakref import ref, ReferenceType

from runtime.reflection.lite.core.objects.member import Member
from runtime.reflection.lite.core.objects.member_collection import MemberCollection, MemberCollectionSubset
from runtime.reflection.lite.core.objects.member_type import MemberType
from runtime.reflection.lite.core.objects.class_ import Class
from runtime.reflection.lite.core.objects.function import Function
from runtime.reflection.lite.core.objects.variable import Variable

class Module(Member):
    __slots__ = [ "__name", "__members", "__modules", "__classes", "__functions", "__properties", "__variables", "__reflected" ]

    def __init__(
        self,
        name: str,
        members: MemberCollection,
        reflected: ModuleType,
    ):
        super().__init__(MemberType.MODULE)
        self.__name = name
        self.__members = members
        self.__modules: MemberCollectionSubset[Module] | None = None
        self.__classes: MemberCollectionSubset[Class] | None = None
        self.__functions: MemberCollectionSubset[Function] | None = None
        self.__variables: MemberCollectionSubset[Variable] | None = None
        self.__reflected = ref(reflected)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def members(self) -> MemberCollection:
        """The class members
        """
        return self.__members

    @property
    def reflected(self) -> ReferenceType[ModuleType]:
        """The module reflected (weak reference).
        """
        return self.__reflected

    @property
    def modules(self) -> MemberCollectionSubset[Module]:
        """The class' nested modules
        """
        if self.__modules is None:
            self.__modules = self.__members.subset_modules()
        else:
            pass # pragma: no cover
        return self.__modules

    @property
    def classes(self) -> MemberCollectionSubset[Class]:
        """The class' nested classes
        """
        if self.__classes is None:
            self.__classes = self.__members.subset_classes()
        else:
            pass # pragma: no cover
        return self.__classes

    @property
    def functions(self) -> MemberCollectionSubset[Function]:
        """The class functions
        """
        if self.__functions is None:
            self.__functions = self.__members.subset_functions()
        else:
            pass # pragma: no cover
        return self.__functions

    @property
    def variables(self) -> MemberCollectionSubset[Variable]:
        """The class fields
        """
        if self.__variables is None:
            self.__variables = self.__members.subset_variables()
        else:
            pass # pragma: no cover
        return self.__variables

    def __repr__(self) -> str:
        return f"{self.name}"