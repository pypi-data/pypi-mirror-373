# pyright: basic
# ruff: noqa
from typing import Any, TypeVar, cast
from pytest import raises as assert_raises, fixture
import sys
from os import getenv

from typingutils import get_generic_parameters, is_generic_function, AnyFunction, TypeArgs
from typingutils.internal import get_executing_function
from typingutils.core.attributes import TYPE_PARAMS

TESTS_EXTENSIVE_DEBUGGING = getenv("TESTS_EXTENSIVE_DEBUGGING", "").lower() in ("1", "true")

def test_is_generic_function():

    def generic_function(arg: int) -> int:
        ...

    assert not is_generic_function(generic_function)

    # generic functions are available in python 3.12
    setattr(generic_function, TYPE_PARAMS, ())

    assert not is_generic_function(generic_function)

    setattr(generic_function, TYPE_PARAMS, (TypeVar("T"),))

    assert is_generic_function(generic_function)


def test_get_executing_function():

    def test_function(arg1: int, arg2: int) -> tuple[AnyFunction, TypeArgs] | None:
        if fn := get_executing_function():
            args = get_generic_parameters(fn)
            return fn, args


    assert not is_generic_function(test_function)

    result = test_function(1,2)

    assert result

    fn, args = result

    assert fn is test_function
    assert not args # this is not a generic function (which is not available until python 3.12)


    def generic_function(arg1: int, arg2: int) -> tuple[AnyFunction, TypeArgs] | None:
        if fn := get_executing_function():
            args = get_generic_parameters(fn)
            return fn, args

    setattr(generic_function, TYPE_PARAMS, (TypeVar("T"),))

    result = generic_function(1,2)

    assert result

    fn, args = result

    assert fn is generic_function
    assert args # this is not a generic function (which is not available until python 3.12)
