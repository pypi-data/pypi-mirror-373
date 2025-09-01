# pyright: basic
# ruff: noqa
from typing import Any, Type, Iterable, TypeVar, Generic, Literal, Annotated, cast
from collections import abc, deque, defaultdict, OrderedDict, ChainMap
from types import NoneType
from pytest import raises as assert_raises, fixture
from enum import Enum
from os import getenv

from typingutils import issubclass_typing, get_type_name, get_type_name, TypeParameter, UnionParameter

from tests.other_impl.issubclass import comparison_generator
from tests.testcase_generators.issubclass import create_testcases_for_issubclass
from tests.generic_classes import DerivedClass1, DerivedClass2, ParentClass, BaseClass, Enumeration

TESTS_EXTENSIVE_DEBUGGING = getenv("TESTS_EXTENSIVE_DEBUGGING", "").lower() in ("1", "true")

subclass_assertions: list[tuple[TypeParameter | tuple[TypeParameter, ...], tuple[TypeParameter | UnionParameter, ...]]] = [
    (type, (
        object,
        Type,
        Type[Any],
        type,
        type[Any])),
    (NoneType, (
        object,
        NoneType,
        Type[Any],
        type[Any])),
    (list, (
        object,
        abc.Collection)),
    (deque, (
        object,
        Type[Any],
        type[Any],
        deque,
        abc.Collection)),
    (dict, (
        object,
        Type[Any],
        type[Any],
        dict,
        abc.Mapping,
        abc.Collection)),
    (defaultdict, (
        object,
        Type[Any],
        type[Any],
        dict,
        defaultdict,
        abc.Mapping,
        abc.MutableMapping,
        abc.Collection)),
    (OrderedDict, (
        object,
        Type[Any],
        type[Any],
        dict,
        OrderedDict,
        abc.Mapping,
        abc.MutableMapping,
        abc.Collection)),
    (ChainMap, (
        object,
        Type[Any],
        type[Any],
        ChainMap,
        abc.Mapping,
        abc.MutableMapping,
        abc.Collection)),
    (set, (
        object,
        Type[Any],
        type[Any],
        set,
        abc.Set,
        abc.Collection)),
    (frozenset, (
        object,
        Type[Any],
        type[Any],
        abc.Set,
        abc.Collection)),
    (tuple, (
        object,
        Type[Any],
        type[Any],
        tuple)),
    (tuple[str], (
        object,
        Type[Any],
        type[Any],
        tuple[Any],
        tuple)),
    ((str, int, float, bool), (
        object,
        Type[Any],
        type[Any],
        (str, int, float, bool)
    )),
    (DerivedClass2, (
        ParentClass,
        BaseClass
    )),
    (Enumeration, (
        object,
        Enum
    ))
]

all_types = set([ type_ for _, types in subclass_assertions for type_ in types ])

@fixture(scope = "module")
def comparisons():
    impl: dict[str, list[tuple[str, str]]] = defaultdict(lambda: [])
    yield impl

    if getenv("TESTS_EXTENSIVE_DEBUGGING", "").lower() in ("1", "true"):
        print("\n")

        for key in impl:
            count = 0
            failed = 0
            for comparison, result in impl[key]:
                if "Error" in result:
                    failed += 1
                    print(f"{comparison} ==> FAILED")
                else:
                    print(f"{comparison} ==> {result}")
                    count +=1

            print(f"Comparison with {key}: {count} differences and {failed} failed\n")


issubclass_testcases = list(create_testcases_for_issubclass())

def test_multiple_bases(comparisons: dict[str, list[tuple[str, str]]]):
    assert issubclass_typing(DerivedClass2, ParentClass)
    assert issubclass_typing(DerivedClass2, BaseClass)
    assert not issubclass_typing(DerivedClass2, DerivedClass1)

def test_issubclass_typing(comparisons: dict[str, list[tuple[str, str]]]):
    tested_base: set[type[Any]] = set()
    tested_comparison: set[type[Any]] = set()

    assert not issubclass_typing(str|int, tuple)

    for testcase in issubclass_testcases:
        if testcase.base not in tested_base:
            tested_base.add(testcase.base)
            result = issubclass_typing(testcase.base, testcase.base)
            if TESTS_EXTENSIVE_DEBUGGING:
                print(f"Testing issubclass_typing({get_type_name(testcase.base)}, {get_type_name(testcase.base)}) ==> {result}")
            assert result

            for impl, result_comparison in comparison_generator(testcase.base, testcase.base):
                if result != result_comparison:
                    comparisons[impl].append((f"Comparing {impl}.issubclass({get_type_name(testcase.base)}, {get_type_name(testcase.base)})", f"{result_comparison} != {result}"))

        if testcase.comparison not in tested_comparison:
            tested_comparison.add(testcase.comparison)

            result = issubclass_typing(testcase.comparison, testcase.base)

            if testcase.expected_equality:
                if TESTS_EXTENSIVE_DEBUGGING:
                    print(f"Testing issubclass_typing({get_type_name(testcase.comparison)}, {get_type_name(testcase.base)}) ==> {result}")
                assert result
            else:
                if TESTS_EXTENSIVE_DEBUGGING:
                    print(f"Testing !issubclass_typing({get_type_name(testcase.comparison)}, {get_type_name(testcase.base)}) ==> {result}")
                assert not result

            for impl, result_comparison in comparison_generator(testcase.comparison, testcase.base):
                if result != result_comparison:
                    comparisons[impl].append((f"Comparing {impl}.issubclass({get_type_name(testcase.comparison)}, {get_type_name(testcase.base)})", f"{result_comparison} != {result}"))


def test_explicit_assertions(comparisons: dict[str, list[tuple[str, str]]]):
    for test_types, types in subclass_assertions:
        for test_type in cast(Iterable[type], test_types if isinstance(test_types, tuple) else (test_types,)):
            for type_ in types:
                result = issubclass_typing(test_type, type_)


                if TESTS_EXTENSIVE_DEBUGGING:
                    print(f"Testing issubclass_typing({get_type_name(test_type)}, {get_type_name(type_)}) ==> {result}")
                if not result:
                    issubclass_typing(test_type, type_)
                assert result

                for impl, result_comparison in comparison_generator(test_type, type_):
                    if result != result_comparison:
                        comparisons[impl].append((f"Comparing {impl}.issubclass({get_type_name(test_type)}, {get_type_name(type_)})", f"{result_comparison} != {result}"))


def test_tuple_bases(comparisons: dict[str, list[tuple[str, str]]]):
    for cls, base, expected in cast(tuple[tuple[TypeParameter, TypeParameter|tuple[TypeParameter], bool]], (
        (str, (str, int, bool), True),
        (str, (int, bool), False),
        (str, ((int, bool), float), False),
    )):
        result = issubclass_typing(cls, base)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing issubclass_typing({get_type_name(cls)}, {get_type_name(base)}) ==> {result}")
        assert result == expected

        for impl, result_comparison in comparison_generator(cls, base):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.issubclass({get_type_name(cls)}, {get_type_name(base)})", f"{result_comparison} != {result}"))


def test_union_bases(comparisons: dict[str, list[tuple[str, str]]]):
    for cls, base, expected in cast(tuple[tuple[TypeParameter, TypeParameter|tuple[TypeParameter], bool]], (
        (str, int | bool, False),
        (str, str | float, True),
        (str | int, str | int, True),
        (str | int, int | str, True),
        (str | int, str | float, False),
        (str | int, bool | int, False),
    )):
        result = issubclass_typing(cls, base)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing issubclass_typing({get_type_name(cls)}, {get_type_name(base)}) ==> {result}")

        assert result == expected

        for impl, result_comparison in comparison_generator(cls, base):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.issubclass({get_type_name(cls)}, {get_type_name(base)})", f"{result_comparison} != {result}"))


def test_typevars(comparisons: dict[str, list[tuple[str, str]]]):
    for cls, base, expected in (
        (dict[str, int], dict[TypeVar("T1"), TypeVar("T2")], True),
        (dict[str, int], dict[TypeVar("T1", bound=str), TypeVar("T2", bound=int)], True),
        (dict[str, int], dict[TypeVar("T1", bound=bool), TypeVar("T2", bound=int)], False),
        (str, TypeVar("T"), True),
        (str, TypeVar("T", int, str), True),
        (str, TypeVar("T", bound=str), True),
        (str, TypeVar("T", bound=int), False),
    ):

        result = issubclass_typing(cls, base)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing issubclass_typing({get_type_name(cls)}, {get_type_name(base)}) ==> {result}")

        assert result == expected

        for impl, result_comparison in comparison_generator(cls, base):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.issubclass({get_type_name(cls)}, {get_type_name(base)})", f"{result_comparison} != {result}"))


def test_multilevel_types(comparisons: dict[str, list[tuple[str, str]]]):
    for cls, base, expected in (
        (tuple[list[str]], tuple[list[str]], True),
        (tuple[list[str]], tuple[list[int]], False),
        (tuple[list[dict[str, int]]], tuple[list[dict[str, int]]], True),
        (tuple[list[dict[str, int]]], tuple[list[dict[str, bool]]], False),
        (tuple[list[dict[str, set[int]]]], tuple[list[dict[str, set[int]]]], True),
        (tuple[list[dict[str, set[int]]]], tuple[list[dict[str, set[str]]]], False),
    ):

        result = issubclass_typing(cls, base)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing issubclass_typing({get_type_name(cls)}, {get_type_name(base)}) ==> {result}")

        assert result == expected

        for impl, result_comparison in comparison_generator(cls, base):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.issubclass({get_type_name(cls)}, {get_type_name(base)})", f"{result_comparison} != {result}"))


def test_tuples(comparisons: dict[str, list[tuple[str, str]]]):
    for cls, base, expected in (
        (tuple[str], tuple[str], True),
        (tuple[str], tuple[str, ...], False),
        (tuple[str], tuple[str, str], False),
        (tuple[str], tuple[Any], True),
        (tuple[str], tuple[Any, ...], False),
        (tuple[str], tuple[str, str], False),
        (tuple[str], list[str], False),
    ):

        result = issubclass_typing(cls, base)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing issubclass_typing({get_type_name(cls)}, {get_type_name(base)}) ==> {result}")

        assert result == expected

        for impl, result_comparison in comparison_generator(cls, base):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.issubclass({get_type_name(cls)}, {get_type_name(base)})", f"{result_comparison} != {result}"))


def test_literals(comparisons: dict[str, list[tuple[str, str]]]):
    for cls, base, expected in (
        (int, Literal[1,2,3,4], True),
        (str, Literal[1,2,3,4], False),
        (str, Literal["a","b","c"], True),
        (str, Literal["a",2,"c"], True),
        (int, Literal["a",2,"c"], True),
    ):

        result = issubclass_typing(cls, base)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing issubclass_typing({get_type_name(cls)}, {get_type_name(base)}) ==> {result}")

        assert result == expected

        for impl, result_comparison in comparison_generator(cls, base):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.issubclass({get_type_name(cls)}, {get_type_name(base)})", f"{result_comparison} != {result}"))


