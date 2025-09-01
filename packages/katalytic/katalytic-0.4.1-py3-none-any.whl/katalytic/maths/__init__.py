import math

from katalytic._pkg import _UNDEFINED
from katalytic.data.checks import is_iterable, is_iterator, is_number, is_sequence


def L1(a, b):
    """Compute the L1 (Manhattan) distance between two values or sequences.

    Parameters:
        a: The first value or sequence.
        b: The second value or sequence.

    Returns:
        The L1 distance between the two values or sequences.

    Raises:
        ValueError: If the types of a or b are not supported or unexpected.
            - If a or b is neither a number or a sequence.
            - If a and b are sequences and
                - the sequences are empty.
                - the sequences have different lengths.
                - the sequences are nested (contains sub-sequences).
    """
    if isinstance(a, bool):
        raise ValueError(f"Got <a> = {a!r}")
    elif isinstance(b, bool):
        raise ValueError(f"Got <b> = {b!r}")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b)
    elif is_sequence(a) and is_sequence(b):
        if len(a) == 0 and len(b) == 0:
            raise ValueError("Both sequences are empty")
        elif len(a) != len(b):
            raise ValueError(f"The sequences have different lengths: {len(a)} and {len(b)}")
        elif is_sequence(a[0]) or is_sequence(b[0]):
            raise ValueError("Nested sequences are not supported")
        else:
            return sum(L1(ai, bi) for ai, bi in zip(a, b, strict=False))
    else:
        raise ValueError(f"Unknown format: ({type(a).__name__}) {a!r} and ({type(b).__name__}) {b!r}")


def L2(a, b):
    """Compute the L2 (Euclidean) distance between two values or sequences.

    Parameters:
        a: The first value or sequence.
        b: The second value or sequence.

    Returns:
        The L2 distance between the two values or sequences.

    Raises:
        ValueError: If the types of a or b are not supported or unexpected.
            - If a or b is neither a number or a sequence.
            - If a and b are sequences and
                - the sequences are empty.
                - the sequences have different lengths.
                - the sequences are nested (contains sub-sequences).
    """
    if isinstance(a, bool):
        raise ValueError(f"Got <a> = {a!r}")
    elif isinstance(b, bool):
        raise ValueError(f"Got <b> = {b!r}")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.sqrt((a - b) ** 2)
    elif is_sequence(a) and is_sequence(b):
        if len(a) == 0 and len(b) == 0:
            raise ValueError("Both sequences are empty")
        elif len(a) != len(b):
            raise ValueError(f"The sequences have different lengths: {len(a)} and {len(b)}")
        elif is_sequence(a[0]) or is_sequence(b[0]):
            raise ValueError("Nested sequences are not supported")
        elif any(isinstance(ai, bool) or isinstance(bi, bool) for ai, bi in zip(a, b, strict=False)):
            raise ValueError("Got a boolean value in one of the sequences")
        elif all(isinstance(ai, (int, float)) and isinstance(bi, (int, float)) for ai, bi in zip(a, b, strict=False)):
            return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b, strict=False)))
        else:
            raise ValueError(f"Unknown format: ({type(a).__name__}) {a!r} and ({type(b).__name__}) {b!r}")
    else:
        raise ValueError(f"Unknown format: ({type(a).__name__}) {a!r} and ({type(b).__name__}) {b!r}")


def min_max(iterable, *, default=_UNDEFINED, key=None):
    """Find the minimum and maximum values from the given iterable.

    Parameters:
        iterable: An iterable object from which to find the minimum and maximum values.
        default (optional): The default value to return if the iterable is empty.
            If not provided, a ValueError is raised when the iterable is empty.
        key (optional): A callable function that is used to extract a comparison key from each element in the iterable.
            If not provided, the elements themselves are used for comparison.

    Returns:
        A tuple containing the minimum and maximum values from the iterable.

    Raises:
        TypeError: If the iterable is not iterable or if the key is not None or callable.
        ValueError: If the iterable is empty and no default value is provided.
    """
    if not is_iterable(iterable):
        raise TypeError(f"<iterable> expected an iterable, got {type(iterable).__name__}")
    elif not (key is None or callable(key)):
        raise TypeError(f"<key> expected a callable, got {type(key).__name__}")

    if key is None:
        key = lambda x: x

    if is_iterator(iterable):
        iterable = list(iterable)

    if len(iterable) == 0:
        if default is _UNDEFINED:
            raise ValueError("Cannot get the min/max of an empty iterable")
        else:
            return default

    min_ = min(iterable, key=key)
    max_ = max(iterable, key=key)
    return (min_, max_)


def clip(x, min_=float("-inf"), max_=float("+inf")):
    """Clip the value x within the specified minimum and maximum bounds.

    Parameters:
        x: The value to be clipped.
        min_ (optional): The minimum bound. If not provided, negative infinity is used.
        max_ (optional): The maximum bound. If not provided, positive infinity is used.

    Returns:
        The clipped value of x, which is guaranteed to be within the specified bounds.

    Raises:
        TypeError: If x, min_, or max_ is not a number.
    """
    if not is_number(x):
        raise TypeError(f"<x> expected a number, got {type(x).__name__}")
    elif not is_number(min_):
        raise TypeError(f"<min_> expected a number, got {type(min_).__name__}")
    elif not is_number(max_):
        raise TypeError(f"<max_> expected a number, got {type(max_).__name__}")

    return min(max(x, min_), max_)
