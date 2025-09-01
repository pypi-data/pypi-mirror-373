from inspect import stack as get_stack

from typingutils.core.attributes import TYPE_PARAMS
from typingutils.core.types import AnyFunction

def is_generic_function(fn: AnyFunction) -> bool:
    """
    Python 3.12 or newer.

    Indicates whether or not type is a generic function.

    Args:
        fn (AnyFunction): A function.

    Returns:
        bool: A boolean indicating if function is generic or not.
    """

    if hasattr(fn, TYPE_PARAMS):
        from typingutils.core.instances import _extract_args # pyright: ignore[reportPrivateUsage]
        params, *_ = _extract_args(fn)
        if params is not None and any(params):
            return True
    return False

def get_executing_function() -> AnyFunction | None:
    """
    Returns the executing function from within it, enabling retrieval of its generic parameters.

    Returns:
        AnyFunction | None: The function executing
    """
    stack = get_stack()
    name: str | None = None

    for frame in stack[1:]:
        if frame.filename == __file__:
            continue # pragma: no cover

        locals = frame[0].f_locals

        if not name:
            name = frame.function
        elif name in locals:
            return locals[name]

        else:
            break # pragma: no cover

    return None # pragma: no cover
