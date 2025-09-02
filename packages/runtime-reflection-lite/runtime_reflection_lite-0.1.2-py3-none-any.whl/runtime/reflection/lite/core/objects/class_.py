from __future__ import annotations
from typing import Any
from weakref import ref, ReferenceType

from runtime.reflection.lite.core.objects.member import Member
from runtime.reflection.lite.core.objects.member_collection import MemberCollection, MemberCollectionSubset
from runtime.reflection.lite.core.objects.member_type import MemberType
from runtime.reflection.lite.core.objects.constructor import Constructor
from runtime.reflection.lite.core.objects.method import Method
from runtime.reflection.lite.core.objects.property_ import Property
from runtime.reflection.lite.core.objects.field import Field

class Class(Member):
    __slots__ = [ "__name", "__bases", "__members", "__constructor", "__classes", "__methods", "__properties", "__fields", "__delegates", "__reflected" ]

    def __init__(
        self,
        name: str,
        bases: set[type[Any]],
        members: MemberCollection,
        reflected: type[Any]
    ):
        super().__init__(MemberType.CLASS)
        self.__name = name
        self.__bases = bases
        self.__members = members
        self.__reflected = ref(reflected)
        self.__constructor: Constructor | None = None
        self.__classes: MemberCollectionSubset[Class] | None = None
        self.__methods: MemberCollectionSubset[Method] | None = None
        self.__properties: MemberCollectionSubset[Property] | None = None
        self.__fields: MemberCollectionSubset[Field] | None = None
        # self.__delegates: MemberCollectionSubset[Delegate] | None = None

    @property
    def name(self) -> str:
        """The class name.
        """
        return self.__name

    @property
    def bases(self) -> set[type[Any]]:
        """The class bases.
        """
        return self.__bases

    @property
    def members(self) -> MemberCollection:
        """The class members.
        """
        return self.__members

    @property
    def reflected(self) -> ReferenceType[type[Any]]:
        """The type reflected (weak reference).
        """
        return self.__reflected

    @property
    def constructor(self) -> Constructor:
        """The class constructor (i.e. "__init__()" function).
        """
        if not self.__constructor:
            _, self.__constructor = self.__members.subset(Constructor)[0] # there's always exactly one constructor
        else:
            pass # pragma: no cover

        return self.__constructor

    @property
    def classes(self) -> MemberCollectionSubset[Class]:
        """The class' nested classes.
        """
        if self.__classes is None:
            self.__classes = self.__members.subset_classes()
        else:
            pass # pragma: no cover
        return self.__classes

    @property
    def methods(self) -> MemberCollectionSubset[Method]:
        """The class methods.
        """
        if self.__methods is None:
            self.__methods = self.__members.subset_methods()
        else:
            pass # pragma: no cover
        return self.__methods

    @property
    def properties(self) -> MemberCollectionSubset[Property]:
        """The class properties.
        """
        if self.__properties is None:
            self.__properties = self.__members.subset_properties()
        else:
            pass # pragma: no cover
        return self.__properties

    @property
    def fields(self) -> MemberCollectionSubset[Field]:
        """The class fields.
        """
        if self.__fields is None:
            self.__fields = self.__members.subset_fields()
        else:
            pass # pragma: no cover
        return self.__fields

    def __repr__(self) -> str:
        return f"{self.name}"