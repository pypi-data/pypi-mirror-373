"""This module implements meta-programming utilities.

They should be used only when absolutely necessary.
"""

import inspect
from pathlib import Path


def reference_caller_function(*, depth=1):
    """Returns a reference to the calling function, based on the specified depth.

    This function inspects the stack frames to retrieve the function that called it.
    The depth parameter specifies how many frames back to look:
        - a depth of 0 will return the function from which the call is made
        - a depth of 1 (the default) will return the immediate caller
        - a depth of 2 will return the caller's caller, and so on

    Parameters:
        depth (int, optional): The number of stack frames back to inspect to find the calling function. (default: 1)

    Returns:
        function: A reference to the function at the specified depth.

    Raises:
        TypeError: If depth is not an integer.
        ValueError: If depth is less than 0 or more than the number of available stack frames.

    Example:
        >>> def foo():
        ...     caller = reference_caller_function()
        ...     print(f'{caller.__name__}() called foo()')
        ...
        >>> def bar():
        ...     foo()
        ...
        >>> bar()
        bar() called foo()
    """
    # I have to execute the preconditions both here and in extract_call_stack_info() because
    # of the depth+1 operation. Otherwise, I might do `True + 1` which python evaluates to 2
    if not isinstance(depth, int):
        raise TypeError(f"depth must be an integer, not {type(depth).__name__}")
    elif isinstance(depth, bool):
        raise TypeError("depth must be an integer, not bool")
    elif depth < 0:
        raise ValueError(f"depth must be >= 0, not {depth}")

    # reference_caller_function() adds an extra frame to the stack so you should use depth=depth+1
    return extract_call_stack_info(depth=depth + 1)[1]


def extract_call_stack_info(*, depth=0):
    """Returns the file path, caller function reference, and line number, based on the
    specified depth.

    This function inspects the stack frames to retrieve the function that called it.
    The depth parameter specifies how many frames back to look:
        - a depth of 0 will return the function from which extract_call_stack_info() was called
        - a depth of 1 (the default) will return the caller one level up
        - a depth of 2 will return the caller two levels up, and so on

    Parameters:
        depth (int, optional): The number of stack frames to go back. (default: 0)

    Returns:
        tuple: A tuple containing the file path, caller function reference, and line number.

    Raises:
        TypeError: If depth is not an integer.
        ValueError: If depth is less than 0 or more than the number of available stack frames.
    """
    if not isinstance(depth, int):
        raise TypeError(f"depth must be an integer, not {type(depth).__name__}")
    elif isinstance(depth, bool):
        raise TypeError("depth must be an integer, not bool")
    elif depth < 0:
        raise ValueError(f"depth must be >= 0, not {depth}")

    stack = inspect.stack()
    if depth >= len(stack):
        raise ValueError(
            f"You're getting ahead of yourself. There are only {len(stack)} frames in the stack, not {depth}."
        )

    # The stack is ordered from the most recent frame to the oldest frame
    # The most recent frame is this function, so we need to increase the depth by 1
    frame_info = stack[depth + 1]
    caller = frame_info.frame.f_code.co_name
    func = _search(caller, frame_info.frame.f_globals, recursion_limit=1)

    return str(Path(frame_info.filename).resolve()), func, frame_info.lineno


def _search(key, data, recursion_limit):
    func = data.get(key)
    if func:
        return func

    next_level = []
    for k, obj in data.items():
        if k.startswith("__"):
            continue

        obj_2 = getattr(obj, "__dict__", {})
        if key in obj_2:
            return obj_2[key]

        if obj_2:
            next_level.append(obj_2)

    if recursion_limit == 0:
        return None

    for obj in next_level:
        func = _search(key, obj, recursion_limit - 1)
        if func:
            return func
