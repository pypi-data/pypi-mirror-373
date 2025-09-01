# pyright: basic
# ruff: noqa
from typing import (
    Any, Sequence, MutableSequence, List, Mapping, MutableMapping, Dict, Deque,
    Set, Tuple, DefaultDict, OrderedDict as OrderedDict_, FrozenSet, Type, Iterable, cast
)
from os import getenv
from collections import abc, deque, defaultdict, OrderedDict, Counter, ChainMap
from datetime import date, time, datetime
from decimal import Decimal
from types import NoneType
from pytest import raises as assert_raises, fixture

from typingutils import TypeParameter, UnionParameter, AnyType, get_type_name, isinstance_typing, is_type
from typingutils.core.compat.annotations import LiteralString
from tests.other_impl.isinstance import comparison_generator

TESTS_EXTENSIVE_DEBUGGING = getenv("TESTS_EXTENSIVE_DEBUGGING", "").lower() in ("1", "true")

instance_assertions: list[tuple[object | tuple[object], tuple[TypeParameter | UnionParameter, ...], bool]] = [
    (type, (
        object,
        Type[Any],
        type[Any]
        ), False),
    (None, (
        object,
        NoneType,
        Type[Any],
        type[Any]), True),
    ("abcdefg", (
        object,
        Type[Any],
        type[Any],
        str,
        abc.Collection,
        abc.Collection[Any],
        abc.Sequence,
        abc.Sequence[Any],
        Sequence,
        Sequence[Any]), True),
    (123, (
        object,
        Type[Any],
        type[Any],
        int), True),
    (10.12345, (
        object,
        Type[Any],
        type[Any],
        float), True),
    (Decimal(10.12345), (
        object,
        Type[Any],
        type[Any],
        Decimal), True),
    ((True, False), (
        object,
        Type[Any],
        type[Any],
        bool,
        int), True),
    (date(2000, 1, 1), (
        object,
        Type[Any],
        type[Any],
        date), True),
    (time(10, 0, 0), (
        object,
        Type[Any],
        type[Any],
        time), True),
    (datetime(2000, 1, 1, 10, 0, 0), (
        object,
        Type[Any],
        type[Any],
        datetime,
        date), True),
    (([], ["a", "b", "c"]), (
        object,
        Type[Any],
        type[Any],
        list,
        list[Any],
        List,
        List[Any],
        abc.Collection,
        abc.Collection[Any],
        abc.Sequence,
        abc.Sequence[Any],
        abc.MutableSequence,
        abc.MutableSequence[Any],
        Sequence,
        Sequence[Any],
        MutableSequence,
        MutableSequence[Any]), True),
    (deque((1,2,3), maxlen=10), (
        object,
        Type[Any],
        type[Any],
        deque,
        deque[Any],
        Deque,
        Deque[Any],
        abc.Collection,
        abc.Collection[Any],
        abc.Sequence,
        abc.Sequence[Any],
        abc.MutableSequence,
        abc.MutableSequence[Any],
        Sequence,
        Sequence[Any],
        MutableSequence,
        MutableSequence[Any]), True),
    (({}, { "a": 1}), (
        object,
        Type[Any],
        type[Any],
        dict,
        dict[Any, Any],
        Dict,
        Dict[Any, Any],
        abc.Mapping,
        abc.Mapping[Any, Any],
        abc.MutableMapping,
        abc.MutableMapping[Any, Any],
        abc.Collection,
        abc.Collection[Any],
        Mapping,
        Mapping[Any, Any],
        MutableMapping,
        MutableMapping[Any, Any]), True),
    (defaultdict(list), (
        object,
        Type[Any],
        type[Any],
        dict,
        dict[Any, Any],
        defaultdict,
        defaultdict[Any, Any],
        Dict,
        Dict[Any, Any],
        DefaultDict,
        DefaultDict[Any, Any],
        abc.Mapping,
        abc.Mapping[Any, Any],
        abc.MutableMapping,
        abc.MutableMapping[Any, Any],
        abc.Collection,
        abc.Collection[Any],
        Mapping,
        Mapping[Any, Any],
        MutableMapping,
        MutableMapping[Any, Any]), True),
    (OrderedDict(), (
        object,
        Type[Any],
        type[Any],
        dict,
        dict[Any, Any],
        Dict,
        Dict[Any, Any],
        OrderedDict,
        OrderedDict[Any, Any],
        OrderedDict_,
        OrderedDict_[Any, Any],
        abc.Mapping,
        abc.Mapping[Any, Any],
        abc.MutableMapping,
        abc.MutableMapping[Any, Any],
        abc.Collection,
        abc.Collection[Any],
        Mapping,
        Mapping[Any, Any],
        MutableMapping,
        MutableMapping[Any, Any]), True),
    (ChainMap(), (
        object,
        Type[Any],
        type[Any],
        ChainMap,
        ChainMap[Any, Any],
        abc.Mapping,
        abc.Mapping[Any, Any],
        abc.MutableMapping,
        abc.MutableMapping[Any, Any],
        abc.Collection,
        abc.Collection[Any],
        Mapping,
        Mapping[Any, Any],
        MutableMapping,
        MutableMapping[Any, Any]), True),
    ({ 1, 2, 3}, (
        object,
        Type[Any],
        type[Any],
        set,
        set[Any],
        Set,
        Set[Any],
        abc.Set,
        abc.Set[Any],
        abc.Collection,
        abc.Collection[Any]), True),
    (frozenset((1,2,3)), (
        object,
        Type[Any],
        type[Any],
        abc.Set,
        abc.Set[Any],
        abc.Collection,
        abc.Collection[Any],
        FrozenSet,
        FrozenSet[Any]), True),
    ((), (
        object,
        Type[Any],
        type[Any],
        tuple,
        Tuple,
        Tuple[Any],
        Sequence,
        Sequence[Any]), True)
]

all_types = set( type_ for _, types, _ in instance_assertions for type_ in types )
all_instances = tuple( (instance, is_inst) for instances, _, is_inst in instance_assertions for instance in cast(Iterable[object], instances if isinstance(instances, tuple) else (instances,)) )


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


def test_all_types(comparisons: dict[str, list[tuple[str, str]]]):
    for type_ in all_types:
        result = is_type(type_)

        if type_ is object:
            assert not result
        else:
            assert result

        result = isinstance_typing(type_, type_)

        if type_ is object:
            assert result # object is always an instance of object
        else:
            assert not result

        for impl, result_comparison in comparison_generator(type_, type_):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.isinstance({type_}, {get_type_name(type_)})", f"{result_comparison} != {result}"))


def test_all_instances(comparisons: dict[str, list[tuple[str, str]]]):
    assert not isinstance_typing(list)
    assert isinstance_typing(object)
    assert not isinstance_typing(type)
    assert isinstance_typing("abc")
    assert isinstance_typing([1,2,3])

    for instance, is_inst in all_instances:
        result = isinstance_typing(instance)

        if is_inst:
            if TESTS_EXTENSIVE_DEBUGGING:
                print(f"Testing isinstance_typing({instance}) ==> {result}")
            assert result
        else:
            if TESTS_EXTENSIVE_DEBUGGING:
                print(f"Testing !isinstance_typing({instance}) ==> {result}")
            assert not result



def test_explicit_assertions(comparisons: dict[str, list[tuple[str, str]]]):
    for instances, types, is_inst in instance_assertions:
        negations = all_types.difference(types)

        for instance in cast(Iterable[object], instances if isinstance(instances, tuple) else (instances,)):
            for type_ in types:
                result = isinstance_typing(instance, type_)

                if TESTS_EXTENSIVE_DEBUGGING:
                    print(f"Testing isinstance_typing({instance}, {get_type_name(type_)}) ==> {result}")
                assert result is not None
                assert result == True

                for impl, result_comparison in comparison_generator(instance, type_):
                    if result != result_comparison:
                        comparisons[impl].append((f"Comparing {impl}.isinstance({instance}, {get_type_name(type_)})", f"{result_comparison} != {result}"))


            for type_ in negations:
                result = isinstance_typing(instance, type_)
                if TESTS_EXTENSIVE_DEBUGGING:
                    print(f"Testing !isinstance_typing({instance}, {get_type_name(type_)}) ==> {result}")

                assert result is not None
                assert result == False

                for impl, result_comparison in comparison_generator(instance, type_):
                    if result != result_comparison:
                        comparisons[impl].append((f"Comparing {impl}.isinstance({instance}, {get_type_name(type_)})", f"{result_comparison} = {result}"))


def test_multiple(comparisons: dict[str, list[tuple[str, str]]]):
    for obj, cls, expected in cast(tuple[tuple[object, Tuple[TypeParameter|UnionParameter, ...], bool]], (
        ("abc", (str, int, bool), True),
        ("abc", (float, int, bool), False),
        ("abc", (float, int, bool), False),
        ("abc", (float, str|int, bool), True),
    )):

        result = isinstance_typing(obj, cls)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing isinstance_typing({obj}, {cls}) ==> {result}")
        assert result == expected

        for impl, result_comparison in comparison_generator(obj, cls):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.isinstance({obj}, {get_type_name(cast(AnyType, cls))})", f"{result_comparison} != {result}"))

def test_builtin_generic_types(comparisons: dict[str, list[tuple[str, str]]]):
    for obj, cls, expected in cast(tuple[tuple[object, Tuple[TypeParameter|UnionParameter, ...], bool]], (
        ([], list[Any], True),
        ([], list, True),
        ([], list[str], False),
        (["a", "b", "c"], list[Any], True),
        (["a", "b", "c"], list, True),
        (["a", "b", "c"], list[str], False),
        ({}, dict[Any, Any], True),
        ({}, dict, True),
        ({}, dict[str, Any], False),
        ({"a": 1, "b": 2}, dict[Any, Any], True),
        ({"a": 1, "b": 2}, dict, True),
        ({"a": 1, "b": 2}, dict[str, Any], False),
    )):

        result = isinstance_typing(obj, cls)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing isinstance_typing({obj}, {cls}) ==> {result}")
        assert result == expected

        for impl, result_comparison in comparison_generator(obj, cls):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.isinstance({obj}, {get_type_name(cast(AnyType, cls))})", f"{result_comparison} != {result}"))


def test_recursive(comparisons: dict[str, list[tuple[str, str]]]):
    class IterableInt(abc.Iterable):
        def __iter__(self):
            return iter((1, 2, 3))
    class IterableStr(abc.Iterable):
        def __iter__(self):
            return iter(("a", "b", "c"))


    for obj, cls, expected in cast(tuple[tuple[object, Tuple[TypeParameter|UnionParameter, ...], bool]], (
        ("abc", Iterable[str], True),
        (123, Iterable[str], False),
        ((), tuple[Any], False),
        ((), tuple, True),
        ((), tuple[str], False),
        (("a", "b", "c"), list[Any], False),
        (("a", "b", "c"), tuple[Any], False),
        (("a", "b", "c"), tuple[Any, ...], True),
        (("a",), tuple[Any, ...], True),
        (("a", "b", "c"), tuple, True),
        (("a", "b", "c"), tuple[str], False),
        (("a", "b", "c"), tuple[str, ...], True),
        (("a",), tuple[str, ...], True),
        (("a", "b", "c"), tuple[str, str, str], True),
        (("a", "b", "c"), tuple[int], False),
        (("a", "b", "c"), tuple[int, ...], False),
        (("a", "b"), tuple[str, str, str], False),
        ([], list[Any], True),
        ([], list, True),
        ([], list[str], True),
        (["a", "b", "c"], list[Any], True),
        (["a", "b", "c"], list, True),
        (["a", "b", "c"], list[str], True),
        (["a", "b", "c"], list[int], False),
        ({}, dict[Any, Any], True),
        ({}, dict, True),
        ({}, dict[str, Any], True),
        ({"a": 1, "b": 2}, dict[Any, Any], True),
        ({"a": 1, "b": 2}, dict, True),
        ({"a": 1, "b": 2}, dict[str, Any], True),
        ({"a": 1, "b": 2}, dict[str, int], True),
        ({"a": 1, "b": 2}, dict[str, str], False),
        ({"a": 1, "b": 2}, dict[int, int], False),
        ({"a", "b"}, set[Any], True),
        ({"a", "b"}, set[str], True),
        ({"a", "b"}, set[int], False),
        (IterableInt(), Iterable, True),
        (IterableInt(), Iterable[int], True),
        (IterableInt(), Iterable[str], False),
        (IterableStr(), Iterable, True),
        (IterableStr(), Iterable[str], True),
        (IterableStr(), Iterable[int], False),
    )):

        result = isinstance_typing(obj, cls, recursive=True)
        if TESTS_EXTENSIVE_DEBUGGING:
            print(f"Testing isinstance_typing({obj}, {cls}, recursive=True) ==> {result}")
        if result != expected:
            isinstance_typing(obj, cls, recursive=True)
        assert result == expected

        for impl, result_comparison in comparison_generator(obj, cls):
            if result != result_comparison:
                comparisons[impl].append((f"Comparing {impl}.isinstance({obj}, {get_type_name(cast(AnyType, cls))})", f"{result_comparison} != {result}"))

        with assert_raises(Exception):
            isinstance_typing(iter(IterableInt()), Iterable[int], recursive=True)