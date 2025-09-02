# pyright: basic
# ruff: noqa
from typing import Any, List
from types import MappingProxyType
from pytest import raises as assert_raises

from runtime.reflection.lite import (
    ParameterKind, Undefined, Function, Constructor, Variable, Field, Class, Delegate,
    Method, Property, FunctionKind, AccessMode, MemberType, Module, MemberFilter, get_members, reflect
)


from tests.explore import explore
from tests.reflection_classes import Class4, Class5, Class6, Class7, Class8, Class9, Class10, Class11, Class12, Class13, AbstractClass, json, public_function


def test_reflect_class4():
    reflection = reflect(Class4)
    assert set(reflection.members.keys()).issuperset([
        "__prop", "prop", "test_method", "test_classmethod", "test_staticmethod", "__dict__"
    ])

    reflection1 = reflect(Class4)
    assert reflection1 is reflection


def test_reflect_json():
    reflection = reflect(json)
    assert set(reflection.members.keys()).issuperset([
        "load", "loads", "dump", "dumps"
    ])

    reflection1 = reflect(json)
    assert reflection1 is reflection



def test_reflect_class13():
    reflection = reflect(Class13)

    assert set(reflection.members.keys()).issuperset([
        "field1", "field2", "__init__"
    ])

    assert reflection.constructor.signature.parameters[0].parameter_type is int # org annotation is Literal[1,2,3,4] which must resolve to int
    assert reflection.constructor.signature.parameters[1].parameter_type is str # org annotation is Annotated[str, "a string"] which must resolve to str
    assert reflection.properties["field2"][1].property_type is str # org annotation is Annotated[str, "a string"] which must resolve to str