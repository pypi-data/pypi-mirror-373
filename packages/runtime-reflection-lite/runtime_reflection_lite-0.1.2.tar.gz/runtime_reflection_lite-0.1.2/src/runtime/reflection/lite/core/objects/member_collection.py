from __future__ import annotations
from typing import Callable, ItemsView, Iterable, Iterator, Mapping, Generic, TypeVar, cast, overload, TYPE_CHECKING
from collections.abc import ItemsView, ValuesView, KeysView

from runtime.reflection.lite.core.objects.member import Member
from runtime.reflection.lite.core.objects.member_info import MemberInfo
from runtime.reflection.lite.core.objects.deferred_reflection import DeferredReflection
from runtime.reflection.lite.core.objects.function import Function
from runtime.reflection.lite.core.objects.method import Method
from runtime.reflection.lite.core.objects.property_ import Property
from runtime.reflection.lite.core.objects.field import Field
from runtime.reflection.lite.core.objects.variable import Variable

if TYPE_CHECKING:
    from runtime.reflection.lite.core.objects.class_ import Class
    from runtime.reflection.lite.core.objects.module import Module

T = TypeVar("T", bound=Member)

class InternalMemberCollection():

    __slots__ = [ "__members", "__index", "__index_reverse", "__completed" ]

    def __init__(self):
        self.__completed = False
        self.__members: list[Member | DeferredReflection[Member]] = []
        self.__index: dict[str, tuple[MemberInfo, Member | DeferredReflection[Member]]] = {}
        self.__index_reverse: dict[Member | DeferredReflection[Member], list[str]] = {}


    def append(self, name: str, info: MemberInfo, member: Member | DeferredReflection[Member]) -> None:
        """Appends a new member.

        Args:
            name (str): The member name.
            info (MemberInfo): The member info.
            member (Member): The member.

        Raises:
            Exception: An exception is raised, if collection is completed,
            or a member with the same name is already present.
        """
        if self.__completed: # pragma: no cover
            raise Exception("MemberCollection is completed")

        # a member can be present several times with different names, but each name must be unique
        if name in self.__index: # pragma: no cover
            raise Exception(f"Member '{name}' is already present in collection")

        self.__members.append(member)
        self.__index[name] = info, member

        if member not in self.__index_reverse:
            self.__index_reverse[member] = [ name ]
        else:
            self.__index_reverse[member].append(name) # pragma: no cover

    def __contains__(self, obj: object) -> bool:
        return self.__index.__contains__(obj) or self.__index_reverse.__contains__(obj)

    def __len__(self) -> int:
        return self.__members.__len__()

    def complete(self) -> MemberCollection:
        """Completes the collection.

        Returns:
            ReadOnly: readonly representation of the collection.
        """
        from collections import OrderedDict
        self.__index = OrderedDict(sorted(self.__index.items()))
        self.__completed = True
        return MemberCollection(self)


class MemberCollection(Mapping[str, tuple[MemberInfo, Member]]):
    __slots__ = [ "__src" ]

    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, src: InternalMemberCollection) -> None:
        ...
    def __init__(self, src: InternalMemberCollection | None = None):
        self.__src = src or InternalMemberCollection()


    @overload
    def keys(self) -> KeysView[str]:
        ...
    @overload
    def keys(self, predicate: Callable[[MemberInfo], bool]) -> KeysView[str]:
        ...
    def keys(self, predicate: Callable[[MemberInfo], bool] | None = None) -> KeysView[str]:
        index: Mapping[str, tuple[MemberInfo, Member]] = getattr(self.__src, "_InternalMemberCollection__index")
        return KeysView({
            name: info
            for name, (info, _member) in index.items()
            if predicate is None or predicate(info)
        })

    @overload
    def values(self) -> ValuesView[tuple[MemberInfo, Member]]:
        ...
    @overload
    def values(self, predicate: Callable[[MemberInfo], bool]) -> ValuesView[tuple[MemberInfo, Member]]:
        ...
    def values(self, predicate: Callable[[MemberInfo], bool] | None = None) -> ValuesView[tuple[MemberInfo, Member]]:
        index: Mapping[str, tuple[MemberInfo, Member | DeferredReflection[Member]]] = getattr(self.__src, "_InternalMemberCollection__index")
        return ValuesView({
            name: (
                info,
                member() if isinstance(member, DeferredReflection) else member
            )
            for name, (info, member) in index.items()
            if predicate is None or predicate(info)
        })

    @overload
    def items(self) -> ItemsView[str, tuple[MemberInfo, Member]]:
        ...
    @overload
    def items(self, predicate: Callable[[MemberInfo], bool]) -> ItemsView[str, tuple[MemberInfo, Member]]:
        ...
    def items(self, predicate: Callable[[MemberInfo], bool] | None = None) -> ItemsView[str, tuple[MemberInfo, Member]]:
        index: Mapping[str, tuple[MemberInfo, Member | DeferredReflection[Member]]] = getattr(self.__src, "_InternalMemberCollection__index")
        return ItemsView({
            name: (
                info,
                member() if isinstance(member, DeferredReflection) else member
            )
            for name, (info, member) in index.items()
            if predicate is None or predicate(info)
        })

    @overload
    def subset(self, member_class: type[T]) -> MemberCollectionSubset[T]:
        ...
    @overload
    def subset(self, member_class: type[T], predicate: Callable[[MemberInfo], bool]) -> MemberCollectionSubset[T]:
        ...
    def subset(self, member_class: type[T], predicate: Callable[[MemberInfo], bool] | None = None) -> MemberCollectionSubset[T]:
        index: Mapping[str, tuple[MemberInfo, Member]] = getattr(self.__src, "_InternalMemberCollection__index")
        src = {
            name : (info, cast(T, member))
            for name, (info, member) in index.items()
            if info.member_class is member_class and (
                predicate is None or predicate(info)
            )
        }
        return MemberCollectionSubset[T](src)

    def subset_modules(self) -> MemberCollectionSubset[Module]:
        from runtime.reflection.lite.core.objects.module import Module
        return self.subset(Module)

    def subset_classes(self) -> MemberCollectionSubset[Class]:
        from runtime.reflection.lite.core.objects.class_ import Class
        return self.subset(Class)

    def subset_methods(self) -> MemberCollectionSubset[Method]:
        return self.subset(Method)

    def subset_functions(self) -> MemberCollectionSubset[Function]:
        return self.subset(Function)

    def subset_properties(self) -> MemberCollectionSubset[Property]:
        return self.subset(Property)

    def subset_fields(self) -> MemberCollectionSubset[Field]:
        return self.subset(Field)

    def subset_variables(self) -> MemberCollectionSubset[Variable]:
        return self.subset(Variable)

    def __getitem__(self, name: str) -> tuple[MemberInfo, Member]:
        index: Mapping[str, tuple[MemberInfo, Member | DeferredReflection[Member]]] = getattr(self.__src, "_InternalMemberCollection__index")
        info, member = index[name]
        return info, member() if isinstance(member, DeferredReflection) else member

    def __contains__(self, obj: object) -> bool:
        return self.__src.__contains__(obj)

    def __iter__(self) -> Iterator[str]:
        index: Mapping[str, Member] = getattr(self.__src, "_InternalMemberCollection__index")
        yield from index

    def __len__(self) -> int:
        return self.__src.__len__()


class MemberCollectionSubset(Iterable[tuple[MemberInfo, T]], Generic[T]):
    __slots__ = [ "__members", "__src" ]

    def __init__(self, src: Mapping[str, tuple[MemberInfo, T]]):
        self.__src = src
        self.__members = sorted(src.keys())


    def subset(self, predicate: Callable[[MemberInfo], bool] | None) -> MemberCollectionSubset[T]:
        """Subsets this subset using a predicate function.

        Args:
            predicate (Callable[[MemberInfo], bool]): The predicate function.

        Returns:
            MemberCollection.Subset[T]: A new subset
        """
        src = {
            name : (info, member)
            for name, (info, member) in self.__src.items()
            if predicate is None or predicate(info)
        }
        return MemberCollectionSubset[T](src)

    def __iter__(self) -> Iterator[tuple[MemberInfo, T]]:
        for member in self.__members:
            yield self[member]

    @overload
    def __getitem__(self, index: str) -> tuple[MemberInfo, T]:
        """Return the member with the specified name"""
        ...
    @overload
    def __getitem__(self, index: int) -> tuple[MemberInfo, T]:
        """Return the member at the specified index (sorted by name)"""
        ...
    def __getitem__(self, index: str | int) -> tuple[MemberInfo, T]:
        if isinstance(index, str):
            info, member = self.__src.__getitem__(index)
        else:
            info, member = self.__src.__getitem__(self.__members[index])

        return info, cast(T, member() if isinstance(member, DeferredReflection) else member)

    def __contains__(self, obj: object) -> bool:
        return obj in self.__src

    def __len__(self) -> int:
        return self.__members.__len__()