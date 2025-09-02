# pyright: basic
# ruff: noqa
from pytest import raises as assert_raises

from runtime.reflection.lite import ParameterKind, Undefined, get_constructor, get_signature


from tests.explore import explore
from tests.reflection_classes import Class4, Class6, Class5

def test_get_constructor():
    signature1 = get_constructor(dict)
    e1 = explore(signature1)
    assert e1 ==  (
        Undefined,
        [
            ("args", ParameterKind.ARGS, Undefined, Undefined),
            ("kwargs", ParameterKind.KWARGS, Undefined, Undefined),
        ]
    )

    signature2 = get_constructor(Class4)
    e2 = explore(signature2)
    assert e2 ==  (
        Undefined,
        [
            ("args", ParameterKind.ARGS, Undefined, Undefined),
            ("kwargs", ParameterKind.KWARGS, Undefined, Undefined),
        ]
    )

    signature21 = get_signature(Class4().__init__)
    assert signature2 == signature21

    signature3 = get_constructor(Class6)
    e3 = explore(signature3)
    assert e3 ==  (
        Undefined,
        [
            ("args", ParameterKind.ARGS, Undefined, Undefined),
            ("kwargs", ParameterKind.KWARGS, Undefined, Undefined),
        ]
    )

    signature31 = get_signature(Class6().__init__)
    assert signature3 == signature31

    signature4 = get_constructor(Class5)
    e4 = explore(signature4)
    assert e4 ==  (
        Undefined, []
    )

    signature41 = get_signature(Class5().__init__)
    assert signature4 == signature41
