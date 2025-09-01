[![Test](https://github.com/apmadsen/typing-utilities/actions/workflows/python-test.yml/badge.svg)](https://github.com/apmadsen/typing-utilities/actions/workflows/python-test.yml)
[![Coverage](https://github.com/apmadsen/typing-utilities/actions/workflows/python-test-coverage.yml/badge.svg)](https://github.com/apmadsen/typing-utilities/actions/workflows/python-test-coverage.yml)
[![Stable Version](https://img.shields.io/pypi/v/typing-utilities?label=stable&sort=semver&color=blue)](https://github.com/apmadsen/typing-utilities/releases)
![Pre-release Version](https://img.shields.io/github/v/release/apmadsen/typing-utilities?label=pre-release&include_prereleases&sort=semver&color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/typing-utilities)
[![PyPI Downloads](https://static.pepy.tech/badge/typing-utilities/week)](https://pepy.tech/projects/typing-utilities)

# typing-utilities: Runtime reflection and validation of types and generics.

typing-utilities extends Python with the ability to check instances and types of generic types and unions introduced in the `typing` module.

Following is a small example of two of the most usable functions `issubclass_typing` and `isinstance_typing`, but a lot more is to be found in the API section further down...

## Example:

```python
from typing import Generic, TypeVar
from typingutils import issubclass_typing, isinstance_typing

T = TypeVar('T')

class Class1(Generic[T]):
    pass

class_type1 = Class1[str]
class_type2 = Class1[int]

issubclass_typing(class_type1, class_type2) # => False

# next line will fail
issubclass(class_type1, class_type2) # => TypeErrorr: Subscripted generics cannot be used with class and instance checks

class_inst1 = class_type1()
class_inst2 = class_type2()

isinstance_typing(class_inst1, class_type1) # => True
isinstance_typing(class_inst1, class_type2) # => False
isinstance_typing(class_inst2, class_type2) # => True
isinstance_typing(class_inst2, class_type1) # => False

# next line will fail
isinstance(class_inst1, class_type1) # => TypeError: Subscripted generics cannot be used with class and instance checks
```

## Conventions

This project differs from Python and other projects in some aspects:

- Generic subscripted types like `list[str]` are always a subclass of its base type `list` whereas the opposite is not true.
- Any type is a subclass of `type[Any]`.
- `type[Any]` is not an instance of `type[Any]`.
- Builtin types and `typing` types are interchangeable, i.e. `list[T]` is interchangeable with `typing.List[T]` etc.
- Annotations like `typing.Literal` and `typing.Required` are not considered types, but "annotated types", and are therefore not supported in type checks. New function `resolve_annotation()` can be used to resolve these to types before calling `isinstance_typing()`.

## What's not included

### Generic types

It's not the goal of this project to deliver generic types such as generically enforced lists and dicts.

## Full documentation

[Go to documentation](https://github.com/apmadsen/typing-utilities/blob/main/docs/documentation.md)

## Other similar projects

There are other similar projects out there like [typing-utils](https://pypi.org/project/typing-utils/) and [runtype](https://pypi.org/project/runtype/), and while typing-utils is outdated and pretty basic, runtype is very similar to `typing-utilities` when it comes to validation.