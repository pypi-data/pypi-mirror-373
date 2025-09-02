# pyright: basic
# ruff: noqa
from pytest import raises as assert_raises

from runtime.reflection.lite import (
    ParameterKind, Undefined, Function, Constructor, Variable, Field, Class,
    Method, Property, FunctionKind, AccessMode, MemberType, Module, get_members
)

from tests.reflection_classes import Class4, Class5, Class6, Class7, Class8, Class9, Class10, AbstractClass


def test_members_collection():
    members = get_members(Class10)

    assert set(members.keys()).issuperset([
        "__init__"
    ])

    info, member = members["__init__"]
    assert member in members
    assert "__init__" in members.keys()
    assert info in dict(members.values())
    assert dict(members.items())["__init__"][1] is member

    assert len(members) > 0
    assert any(list(iter(members)))
    constructors = members.subset(Constructor)
    assert any(list(iter(constructors)))
    assert len(constructors) == 1
    assert isinstance(constructors.subset(lambda m: m.name == "__init__")[0][1], Constructor)

def test_example_2():
    import runtime.reflection.lite
    from runtime.reflection.lite import MemberFilter, get_members

    members = get_members(runtime.reflection.lite, filter = MemberFilter.CLASSES | MemberFilter.FUNCTIONS_AND_METHODS)
    functions = members.subset_functions()
    classes = members.subset_classes()

    info, member = functions["get_signature"]
    assert info.access_mode == runtime.reflection.lite.AccessMode.PUBLIC
    assert member.kind == runtime.reflection.lite.FunctionKind.FUNCTION

    assert "Member" in classes

def test_example_1():
    from runtime.reflection.lite import MemberFilter, get_signature, get_members

    class Class1:
        def __init__(self, value: str):
            self.__value = value

        def do_something(self, suffix: str | None = None) -> str:
            return self.__value + (suffix or "")

    signature1 = get_signature(Class1.do_something) # -> (suffix: str | None) -> str
    signature2 = get_signature(Class1.__init__) # -> (value: str)

    members = get_members(Class1, filter = MemberFilter.FUNCTIONS_AND_METHODS)
    info, member = members["do_something"] # -> MemberInfo, Method
