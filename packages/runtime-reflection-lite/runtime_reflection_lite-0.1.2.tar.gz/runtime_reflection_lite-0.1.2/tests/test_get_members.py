# pyright: basic
# ruff: noqa
from typing import Any, List
from types import MappingProxyType, GetSetDescriptorType
from pytest import raises as assert_raises

from runtime.reflection.lite import (
    ParameterKind, Undefined, Function, Constructor, Variable, Field, Class, Delegate,
    Method, Property, FunctionKind, AccessMode, MemberType, Module, MemberFilter, get_members
)


from tests.explore import explore
from tests.reflection_classes import Class4, Class5, Class6, Class7, Class8, Class9, Class10, Class11, Class12, AbstractClass, json, public_function


def test_get_members():
    members = get_members(Class4, filter=MemberFilter.CLASSES | MemberFilter.FUNCTIONS_AND_METHODS | MemberFilter.PROPERTIES)
    assert set(members.keys()).issuperset([
        "prop", "test_method", "test_classmethod", "test_staticmethod"
    ])

    members = get_members(Class11, filter=MemberFilter.FIELDS_AND_VARIABLES)
    assert set(members.keys()).issuperset([
        "b"
    ])

    members = get_members(Class11, filter=MemberFilter.FIELDS_AND_VARIABLES | MemberFilter.PROTECTED)
    assert set(members.keys()).issuperset([
        "b", "_b"
    ])

    members = get_members(Class11, filter=MemberFilter.FIELDS_AND_VARIABLES | MemberFilter.PRIVATE)
    assert set(members.keys()).issuperset([
        "b", "_b", "__b"
    ])


def test_get_members_class4():
    members = get_members(Class4)
    assert set(members.keys()).issuperset([
        "__prop", "prop", "test_method", "test_classmethod", "test_staticmethod", "__dict__"
    ])

    info, member = members["__dict__"]
    assert isinstance(member, Delegate)
    assert info.member_class is Delegate
    assert info.member_type == MemberType.DELEGATE
    assert member.parent_cls is Class4
    assert isinstance(member.reflected, GetSetDescriptorType)
    assert issubclass(member.delegate_type, MappingProxyType)


    info, member = members["__prop"]
    assert isinstance(member, Field)
    assert info.member_class is Field
    assert info.member_type == MemberType.FIELD
    assert info.access_mode == AccessMode.PRIVATE
    assert member.parent_cls is Class4
    assert member.field_type == int

    info, member = members["prop"]
    assert isinstance(member, Property)
    assert info.member_class is Property
    assert info.member_type == MemberType.PROPERTY
    assert info.access_mode == AccessMode.PUBLIC
    assert member.getter is not None
    assert member.setter is not None
    assert member.deleter is None
    assert info.parent is Class4
    assert member.bound_cls is Class4
    assert not member.is_readonly
    assert member.property_type == int
    assert member.property_type == member.getter.return_type

    info, member = members["test_method"]
    assert isinstance(member, Method)
    assert info.member_class is Method
    assert info.member_type == MemberType.METHOD
    assert info.access_mode == AccessMode.PUBLIC
    assert member.kind == FunctionKind.METHOD
    assert info.parent == Class4
    assert member.bound_cls is Class4
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["value"].default is Undefined
    assert member.signature.parameters["value"].parameter_type is Any
    assert member.return_type is Any

    info, member = members["test_classmethod"]
    assert isinstance(member, Method)
    assert info.member_class is Method
    assert info.member_type == MemberType.METHOD
    assert info.access_mode == AccessMode.PUBLIC
    assert member.kind == FunctionKind.CLASS_METHOD
    assert info.parent == Class4
    assert member.bound_cls is Class4
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["value"].default is Undefined
    assert member.signature.parameters["value"].parameter_type is Any
    assert member.return_type is Any

    info, member = members["test_staticmethod"]
    assert isinstance(member, Method)
    assert info.member_class is Method
    assert info.member_type == MemberType.METHOD
    assert info.access_mode == AccessMode.PUBLIC
    assert member.kind == FunctionKind.STATIC_METHOD
    assert info.parent == Class4
    assert member.bound_cls is Class4
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["value"].default is Undefined
    assert member.signature.parameters["value"].parameter_type is Any
    assert member.return_type is Any

def test_get_members_class6():
    members = get_members(Class6)
    assert set(members.keys()).issuperset([
        "prop1", "prop2", "prop3", "_test1", "_test2"
    ])

    info, member = members["prop1"]
    assert isinstance(member, Property)
    assert member.setter is None
    assert member.is_readonly
    assert member.property_type == int

    info, member = members["prop2"]
    assert isinstance(member, Property)
    assert member.reflected is Class6.prop2
    assert member.setter is None
    assert member.property_type == int

    info, member = members["prop3"]
    assert isinstance(member, Property)
    assert member.setter is None
    assert member.property_type == int

    info, member = members["_test1"]
    assert isinstance(member, Method)
    assert info.access_mode == AccessMode.PROTECTED
    assert member.kind == FunctionKind.METHOD
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["x"].default is Undefined
    assert member.signature.parameters["x"].parameter_type == str|int
    assert member.return_type == bool

    info, member = members["_test2"]
    assert isinstance(member, Method)
    assert info.access_mode == AccessMode.PROTECTED
    assert member.kind == FunctionKind.METHOD
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["x"].default == [ "test" ]
    assert member.signature.parameters["x"].parameter_type == List[str]
    assert member.return_type == None


def test_get_members_class7():
    members = get_members(Class7)
    assert set(members.keys()).issuperset([
        "__init__", "value", "do_something1", "do_something2", "do_something3",
        "_semi_private_function", "__private_function"
    ])

    info, member = members["value"]
    assert isinstance(member, Property)
    assert member.setter is not None
    assert not member.is_readonly
    assert member.property_type == str

    info, member = members["__init__"]
    assert isinstance(member, Constructor)
    assert member.kind == FunctionKind.CONSTRUCTOR
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["value"].default is Undefined
    assert member.signature.parameters["value"].parameter_type == str
    assert member.return_type == Undefined

    info, member = members["do_something1"]
    assert isinstance(member, Method)
    assert member.kind == FunctionKind.METHOD
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["suffix"].default == None
    assert member.signature.parameters["suffix"].parameter_type == str | None
    assert member.return_type == str

    info, member = members["do_something2"]
    assert isinstance(member, Method)
    assert member.kind == FunctionKind.CLASS_METHOD
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["y"].default == Undefined
    assert member.signature.parameters["y"].parameter_type == float
    assert member.return_type == str

    info, member = members["do_something3"]
    assert isinstance(member, Method)
    assert member.kind == FunctionKind.STATIC_METHOD
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["x"].default == Undefined
    assert member.signature.parameters["x"].parameter_type == int
    assert member.return_type == None

    info, member = members["_semi_private_function"]
    assert isinstance(member, Method)
    assert info.access_mode == AccessMode.PROTECTED
    assert member.kind == FunctionKind.METHOD
    assert len(member.signature.parameters) == 0
    assert member.return_type == None

    info, member = members["__private_function"]
    assert isinstance(member, Method)
    assert info.org_name == "_Class7__private_function"
    assert info.access_mode == AccessMode.PRIVATE
    assert member.kind == FunctionKind.METHOD
    assert len(member.signature.parameters) == 0
    assert member.return_type == None


def test_get_members_class10():
    members = get_members(Class10)

    assert set(members.keys()).issuperset([
        "__init__"
    ])

    info, member = members["__init__"]
    assert isinstance(member, Constructor)
    assert info.member_type == MemberType.METHOD
    assert info.is_special
    assert info.is_inherited
    assert info.access_mode == AccessMode.PUBLIC
    assert member.kind == FunctionKind.CONSTRUCTOR
    assert len(member.signature.parameters) == 1
    assert member.signature.parameters["x"].default is Undefined
    assert member.signature.parameters["x"].parameter_type == int
    assert member.return_type == Undefined

def test_get_members_class12():
    members = get_members(Class12)

    assert set(members.keys()).issuperset([
        "b", "_b", "__b"
    ])


def test_get_members_abstractclass():
    members = get_members(AbstractClass)
    assert set(members.keys()).issuperset([
        "prop1", "prop2", "prop3", "_test1", "_test2", "_test3", "_test4", "_test5"
    ])

    for info, member in ( members[member] for member in ( "prop2", "prop3", "_test1", "_test2", "_test3", "_test4", "_test5" )):
        if isinstance(member, Property):
            assert member.is_abstract
        elif isinstance(member, Method):
            assert member.is_abstract
        else:
            x=0

def test_get_members_module():
    from tests import reflection_classes
    members = get_members(reflection_classes)
    assert set(members.keys()).issuperset([
        "Class1", "Class2", "Class3", "Class4", "ClassBaseA", "ClassBaseB",
        "WithDelegate", "ClassDerived", "Class5", "Class6", "AbstractClass", "Class7",
        "Class8", "Class9", "Class10", "public_function", "_semi_private_function", "__private_function",
        "Variable1", "Variable2", "Variable3", "class10", "datetime"
    ])

    for cls in ("Class1", "Class2", "Class3", "Class4", "ClassBaseA", "ClassBaseB",
        "WithDelegate", "ClassDerived", "Class5", "Class6", "AbstractClass", "Class7",
        "Class8", "Class9", "Class10"):

        info, member = members[cls]
        assert info.member_class is Class
        assert isinstance(member, Class)
        assert member.member_type == MemberType.CLASS


    info, member = members["reflection_modules"]
    assert isinstance(member, Module)
    assert info.member_class is Module
    assert member.members["json"] == member.modules["json"]

    info, member = members["datetime"]
    assert isinstance(member, Module)
    assert info.member_class is Module
    assert member.name == "datetime"
    assert member.member_type == MemberType.MODULE
    assert member.members["datetime"] == member.classes["datetime"]
    assert member.members["MAXYEAR"] == member.variables["MAXYEAR"]
    x=members.subset_modules()

    info, member = members["json"]
    assert isinstance(member, Module)
    assert member.reflected() is json
    assert info.member_class is Module
    assert member.members["loads"] == member.functions["loads"]

    info, member = members["Class5"]
    assert isinstance(member, Class)
    assert member.reflected() is Class5
    assert object in member.bases
    assert member.name == "Class5"
    assert member.constructor is member.members["__init__"][1]
    assert member.classes["SubClass"][1] is member.members["SubClass"][1]
    assert member.methods["test"][1] is member.members["test"][1]
    assert member.properties["prop1"][1] is member.members["prop1"][1]
    assert member.fields["field1"][1] is member.members["field1"][1]
    assert "field2" in member.fields # field without value
    assert member.constructor.bound_cls is Class5

    info, member = members["Class10"]
    assert isinstance(member, Class)
    assert member.name == "Class10"
    assert member.bases.issuperset((Class8, Class9))

    info, member = members["class10"]
    assert isinstance(member, Variable)
    assert info.name == "class10"

    info, member = members["datetime"]
    assert isinstance(member, Module)

    info, member = members["Variable1"]
    assert isinstance(member, Variable)
    assert member.member_type == MemberType.VARIABLE
    assert member.variable_type == int | None

    info, member = members["Variable2"]
    assert isinstance(member, Variable)
    assert member.member_type == MemberType.VARIABLE
    assert member.variable_type == str | None

    info, member = members["Variable3"]
    assert isinstance(member, Variable)
    assert member.member_type == MemberType.VARIABLE
    assert member.variable_type == float

    info, member = members["public_function"]
    assert isinstance(member, Function)
    assert member.reflected() is public_function
    assert member.kind == FunctionKind.FUNCTION
    assert len(member.signature.parameters) == 0
    assert member.return_type == None

    info, member = members["_semi_private_function"]
    assert isinstance(member, Function)
    assert info.access_mode == AccessMode.PROTECTED
    assert member.kind == FunctionKind.FUNCTION
    assert len(member.signature.parameters) == 0
    assert member.return_type == None

    info, member = members["__private_function"]
    assert isinstance(member, Function)
    assert info.org_name == "__private_function"
    assert info.access_mode == AccessMode.PRIVATE
    assert member.kind == FunctionKind.FUNCTION
    assert len(member.signature.parameters) == 0
    assert member.return_type == None
