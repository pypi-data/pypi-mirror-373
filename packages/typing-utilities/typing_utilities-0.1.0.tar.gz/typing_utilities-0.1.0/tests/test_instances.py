# pyright: basic
# ruff: noqa
from typing import (
    Generic, Tuple, Dict, Optional, Union, Any, Literal, Annotated, cast,
    ClassVar, Final, TypeAlias
)
from datetime import date, time, datetime
from pytest import raises as assert_raises
from os import getenv

from typingutils import isinstance_typing, issubclass_typing, get_generic_arguments, get_generic_parameters, is_literal, is_annotated_type, resolve_annotation, get_type_name
from typingutils.internal import get_original_class
from typingutils.core.types import ANNOTATIONS
from typingutils.core.compat.annotations import ReadOnly, Required, NotRequired, LiteralString, Unpack
from typingutils.core.compat.annotations import LiteralString

from tests.generic_classes import NormalClass, GenericClass1, T, T1, T2
from tests.generic_types import non_generic_types, generic_types

TESTS_EXTENSIVE_DEBUGGING = getenv("TESTS_EXTENSIVE_DEBUGGING", "").lower() in ("1", "true")

def test_get_original_class():
    class GenericClass(Generic[T]):
        def __new__(cls, *args: Any, **kwargs: Any):
            cls.clsorig = get_original_class(cls)
            return object.__new__(cls, *args, **kwargs)
        def __init__(self):
            self.orig = get_original_class(self)

    for inst, override_fn, expected, test_negation in cast(tuple[tuple[object, bool, type[Any], bool], ...], (
        (GenericClass[str]().clsorig, False, GenericClass[str],True),
        (GenericClass[str]().orig, False, GenericClass[str],True),
        (GenericClass[str](), True, GenericClass[str],True),
        (list[str](), True, list, False), # builtin generic types aren't supported
    )):
        if test_negation:
            assert type(inst) != expected
        result = get_original_class(inst) if override_fn else inst
        assert result == expected


def test_get_generic_arguments():
    class GenericClass(Generic[T]):
        def __new__(cls, *args: Any, **kwargs: Any):
            cls.clsargs = get_generic_arguments(cls)
            return object.__new__(cls, *args, **kwargs)

        def __init__(self):
            self.args = get_generic_arguments(self)
            x=0

        @property
        def test(self) -> str:
            args = get_generic_arguments(self)
            return str(args)

    for inst, override_fn, expected in cast(tuple[tuple[object, bool, tuple[Any, ...]], ...], (
        (GenericClass[str], True, (str,)),
        (GenericClass[str](), True, (str,)),
        (GenericClass[str]().args, False, (str,)),
        (GenericClass[str]().clsargs, False, (str,)),
        (str, True, ()),
        ("", True, ()),
    )):
        result = get_generic_arguments(inst) if override_fn else inst
        assert result == expected



def test_isinstance_typing():
    classes_simple: dict[type[Any], list[Any]] = {
        str: [ "test", "" ],
        bool: [ True, False ],
        int: [ 1, 2, 3 ],
        float: [ 1.1, 1.2, 1.3 ],
        date: [ datetime.today() ],
        time: [ datetime.now().time() ],
        datetime: [ datetime.now() ]
    }

    for cls, examples in classes_simple.items():
        for example in examples:
            assert isinstance_typing(example, cls)

    assert isinstance_typing("dsfhfdg", (str, int))
    assert isinstance_typing(NormalClass, type)
    assert not isinstance_typing(GenericClass1[int](), GenericClass1[str])
    assert isinstance_typing(GenericClass1[str](), GenericClass1[str])
    assert not isinstance_typing(T, str)
    assert isinstance_typing("abc", Union[int, str])
    assert not isinstance_typing("abc", Union[int, float])
    assert not isinstance_typing(None, Union[int, str])
    assert isinstance_typing("abc", Union[str, None])
    assert isinstance_typing("abc", Optional[str])
    assert isinstance_typing(None, Union[str, None])
    assert isinstance_typing(None, Optional[str])
    assert not isinstance_typing(list[str], type)
    assert not isinstance_typing(list[str], str)
    assert not isinstance_typing(list[str], list[str])
    assert isinstance_typing("abc", int|str)
    assert not isinstance_typing("abc", int|float)
    assert not isinstance_typing(None, int|str)
    assert isinstance_typing("abc", str|None)
    assert isinstance_typing(None, str|None)

    for cls in ANNOTATIONS:
        assert not isinstance_typing(str, cls)


def test_issubclass_typing():

    assert not issubclass_typing(Tuple, Tuple[str, ...])
    assert issubclass_typing(Dict[str, int], Dict[T1, T2]) # pyright: ignore[reportGeneralTypeIssues]

    with assert_raises(ValueError):
        assert not issubclass_typing(T, T) # pyright: ignore[reportCallIssue, reportArgumentType]
    with assert_raises(ValueError):
        assert not issubclass_typing(T1, T2) # pyright: ignore[reportCallIssue, reportArgumentType]
    with assert_raises(ValueError):
        assert not issubclass_typing(T, str) # pyright: ignore[reportCallIssue, reportArgumentType]

def test_is_literal():
    tests = (
        (Literal[1,2,3], True),
        (Literal[1,"a",3], True),
        (str, False),
    )
    for test, expected in tests:
        result = is_literal(test)

        assert result == expected

    for cls in (*generic_types, *non_generic_types):
        result = is_literal(cls)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing is_literal({get_type_name(cls)}) ==> {result}")
        assert not result

def test_is_annotation():
    tests = (
        (Annotated[int, "test"], True),
        (Required[int], True),
        (ReadOnly[int], True),
        (NotRequired[int], True),
        (ClassVar[int], True),
        (Final[int], True),
        (Unpack[int], True),
        (Literal[1,"a",3], True),
        (LiteralString, True),
        (str, False),
    )
    for test, expected in tests:
        result = is_annotated_type(test)

        assert result == expected

    for cls in (*generic_types, *non_generic_types):
        result = is_literal(cls)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing is_annotated_type({get_type_name(cls)}) ==> {result}")
        assert not result


def test_resolve_annotation():
    tests = (
        (str, str),
        (str|int, str|int),
        (float|bool, float|bool),
        (Literal[1,2,3], int),
        (Literal[1,"a",3], int|str),
        (Literal["a"], str),
        (LiteralString, str),
        (Required[int], int),
        (ReadOnly[int], int),
        (NotRequired[int], int),
        (ClassVar[int], int),
        (Final[int], int),
        (Annotated[int, "an integer"], int),
        (Annotated[float|int, "an integer or float"], float|int),
    )
    for test, expected in tests:
        result = resolve_annotation(test)

        if result != expected:
            resolve_annotation(test)
        assert result == expected
