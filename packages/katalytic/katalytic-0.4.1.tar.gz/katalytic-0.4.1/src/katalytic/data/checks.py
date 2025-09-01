"""This module contains various utility functions for checking and comparing data.

- checking the type
- checking the structure
- checking if two collections share some values or properties

Examples:
    >>> contains_any_of([1, 2, 3], [1, True, None])
    True
    >>> is_sequence_of_dicts([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])
    True
    >>> is_singleton(True)
    True
    >>> is_singleton(None)
    True
"""

import collections
import inspect
import os
from decimal import Decimal
from fractions import Fraction


def contains_all_of(haystack, needles):
    """Check if all the needles are present in the haystack.

    Args:
        haystack (iterable):
            The iterable to search in.
        needles (iterable):
            The iterable containing elements to search for.

    Returns:
        bool:
            True if all elements in needles are found in the haystack, False otherwise.

    Raises:
        TypeError:
            If either haystack or needles is not an iterable.

    Examples:
        >>> contains_all_of([4, True, None, 1, 3], [1, True, 3])
        True
        >>> contains_all_of([1, 2, True], [1, 2, 3])
        False
    """
    if not is_iterable(haystack):
        raise TypeError(f"<haystack> expects an iterable. Got {type(haystack).__name__}: {haystack!r}")
    elif not is_iterable(needles):
        raise TypeError(f"<needles> expects an iterable. Got {type(needles).__name__}: {needles!r}")

    for needle in needles:
        if not is_any_of(needle, haystack):
            return False

    return True


def contains_any_of(haystack, needles):
    """Check if any needle is present in the haystack.

    Args:
        haystack (iterable):
            The iterable to search in.
        needles (iterable):
            The iterable containing elements to search for.

    Returns:
        bool:
            True if at least one element in needles is found in the haystack, False otherwise.

    Raises:
        TypeError:
            If either haystack or needles is not an iterable.

    Examples:
        >>> contains_any_of([1, 2, 3], [1, True, None])
        True
        >>> contains_any_of([1, True, 3], [4, True, None])
        True
        >>> contains_any_of([1, 2, 3], [4, True, None])
        False
    """
    if not is_iterable(haystack):
        raise TypeError(f"<haystack> expects an iterable. Got {type(haystack).__name__}: {haystack!r}")
    elif not is_iterable(needles):
        raise TypeError(f"<needles> expects an iterable. Got {type(needles).__name__}: {needles!r}")

    for needle in needles:
        if is_any_of(needle, haystack):
            return True

    return False


def contains_none_of(haystack, needles):
    """Check if none of the needles are present in the haystack.

    Args:
        haystack (iterable):
            The iterable to search in.
        needles (iterable):
            The iterable containing elements to search for.

    Returns:
        bool:
            True if none of the elements in needles are found in the haystack, False otherwise.

    Examples:
        >>> contains_none_of([1, 2, 3], [4, True, None])
        True
        >>> contains_none_of([1, 2, 3], [1, True, None])
        False
        >>> contains_none_of([1, True, 3], [4, True, None])
        False
    """
    return not contains_any_of(haystack, needles)


def dicts_share_key_order(dict_1, dict_2, recursive=False):
    """Check if two dictionaries share the same key order.

    Args:
        dict_1 (dict):
            The first dictionary.
        dict_2 (dict):
            The second dictionary.
        recursive (bool, optional):
            Specifies whether to recursively compare nested dictionaries. Defaults to False.

    Returns:
        bool:
            True if the dictionaries share the same key order, False otherwise.

    Raises:
        TypeError:
            If recursive is not a boolean value or if the types of dict_1 and dict_2 are not compatible.

    Examples:
        >>> dicts_share_key_order({'a': 1, 'b': 2}, {'a': 3, 'b': 4})
        True
        >>> dicts_share_key_order({'a': 1, 'b': 2}, {'c': 1, 'd': 2})
        False
        >>> dicts_share_key_order({'a': 1, 'b': 2}, {'c': 1})
        False
    """
    if not isinstance(recursive, bool):
        raise TypeError(f"<dict_2> must be True or False. Got {type(recursive)}")

    if isinstance(dict_1, dict):
        if not isinstance(dict_2, dict):
            raise TypeError(f"<dict_2> must be a dict. Got {type(dict_2)}")

        if list(dict_1.keys()) != list(dict_2.keys()):
            return False

        if recursive:
            return all(
                dicts_share_key_order(v_1, v_2, recursive=recursive)
                for v_1, v_2 in zip(dict_1.values(), dict_2.values(), strict=False)
            )
        else:
            return True
    elif recursive and is_sequence(dict_1):
        if not is_sequence(dict_2):
            raise TypeError(f"<dict_2> must be a sequence. Got {type(dict_2)}")

        return all(
            dicts_share_key_order(d_1, d_2, recursive=recursive) for d_1, d_2 in zip(dict_1, dict_2, strict=False)
        )
    elif not recursive:
        raise TypeError(f"<dict_1> and <dict_2> must be dicts. Got {type(dict_1)} and {type(dict_2)}")
    else:
        return True


def dicts_share_value_order(dict_1, dict_2, recursive=False):
    """Check if two dictionaries share the same value order.

    Args:
        dict_1 (dict):
            The first dictionary.
        dict_2 (dict):
            The second dictionary.
        recursive (bool, optional):
            Specifies whether to recursively compare nested dictionaries. Defaults to False.

    Returns:
        bool:
            True if the dictionaries share the same value order, False otherwise.

    Raises:
        TypeError:
            If recursive is not a boolean value or if the types of dict_1 and dict_2 are not compatible.

    Examples:
        >>> dicts_share_value_order({'a': 1, 'b': 2}, {'c': 1, 'd': 2})
        True
        >>> dicts_share_value_order({'a': 1, 'b': 2}, {'c': 1, 'd': 3})
        False
        >>> dicts_share_value_order({'a': 1, 'b': 2}, {'c': 1})
        False
    """
    if not isinstance(recursive, bool):
        raise TypeError(f"<dict_2> must be True or False. Got {type(recursive)}")

    if isinstance(dict_1, dict):
        if not isinstance(dict_2, dict):
            raise TypeError(f"<dict_2> must be a dict. Got {type(dict_2)}")

        if list(dict_1.values()) != list(dict_2.values()):
            return False

        if recursive:
            return all(
                dicts_share_value_order(v_1, v_2, recursive=recursive)
                for v_1, v_2 in zip(dict_1.values(), dict_2.values(), strict=False)
            )
        else:
            return True
    elif recursive and is_sequence(dict_1):
        return all(
            dicts_share_value_order(d_1, d_2, recursive=recursive) for d_1, d_2 in zip(dict_1, dict_2, strict=False)
        )
    elif not recursive:
        raise TypeError(f"<dict_1> and <dict_2> must be dicts. Got {type(dict_1)} and {type(dict_2)}")
    else:
        return True


def is_any_of(needle, haystack):
    """Check if the needle is in the haystack. This correctly compares singletons (None,
    True, False) using `is` and other values using `==`.

    Args:
        needle (Any):
            The value to compare against the elements in the haystack.
        haystack (Iterable):
            The iterable containing the elements to compare with the needle.

    Returns:
        bool:
            True if the needle is equal to any element in the haystack, False otherwise.

    Raises:
        TypeError:
            If the haystack is not an iterable.

    Examples:
        >>> is_any_of(1, [1, 2, 3])
        True
        >>> is_any_of(0, [1, 2, 3])
        False
        >>> is_any_of(True, [1, 2, 3])
        False
    """
    if not is_iterable(haystack):
        raise TypeError(f"<haystack> expects an iterable. Got {type(haystack).__name__}: {haystack!r}")

    return any(is_equal(needle, x) for x in haystack)


def is_dict_of_sequences(x, *, empty_ok=True):
    """Check if the input is a dictionary where all values are sequences.

    Args:
        x (Any): The input to check.
        empty_ok (bool, optional): Specifies whether an empty dictionary is allowed. Defaults to True.

    Returns:
        bool: True if the input is a dictionary and all values are sequences,
            False otherwise.

    Examples:
        >>> is_dict_of_sequences({'a': [1, 2], 'b': [3, 4]})
        True
        >>> is_dict_of_sequences({'a': [1, 2], 'b': [3, 4, 5]})
        True
        >>> is_dict_of_sequences({'a': [1, 2], 'b': 100})
        False
        >>> is_dict_of_sequences([{'a': 1}, {'a': 2}])
        False
        >>> is_dict_of_sequences({}, empty_ok=False)
        False
        >>> is_dict_of_sequences({}, empty_ok=True)
        True
    """
    if not isinstance(empty_ok, bool):
        raise TypeError(f"<empty_ok> expects False or True. Got {type(empty_ok)}")

    if isinstance(x, dict):
        if (len(x) >= 1 and all(is_sequence(v) for v in x.values())) or (len(x) == 0 and empty_ok):
            return True

    return False


def is_dict_of_sequences_uniform(x, *, empty_ok=True):
    """Check if the input is a dictionary where all values are sequences of the same
    length.

    Args:
        x (Any): The input to check.
        empty_ok (bool, optional): Specifies whether an empty dictionary is allowed. Defaults to True.

    Returns:
        bool: True if the input is a dictionary and all values are sequences of the same length,
            False otherwise.

    Examples:
        >>> is_dict_of_sequences_uniform({'a': [1, 2], 'b': [3, 4]})
        True
        >>> is_dict_of_sequences_uniform({'a': [], 'b': []})
        True
        >>> is_dict_of_sequences_uniform({'a': [1, 2], 'b': [3]})
        False
        >>> is_dict_of_sequences_uniform({'a': [1, 2], 'b': [3, 4, 5]})
        False
        >>> is_dict_of_sequences_uniform({}, empty_ok=False)
        False
        >>> is_dict_of_sequences_uniform({}, empty_ok=True)
        True
    """
    if not is_dict_of_sequences(x, empty_ok=empty_ok):
        return False
    elif len(x) == 0 and empty_ok:
        return True

    n = len(list(x.values())[0])
    return all(len(v) == n for v in x.values())


def is_equal(a, b):
    """Check if two objects are equal. This correctly compares singletons (None, True,
    False) using `is` and other values using `==`.

    Args:
        a (Any): The first object.
        b (Any): The second object.

    Returns:
        bool: True if the objects are equal, False otherwise.

    Examples:
        >>> is_equal(1, 1)
        True
        >>> is_equal(False, False)
        True
        >>> is_equal(1, True)
        False
        >>> is_equal(1, 2)
        False
    """
    if is_singleton(a) or is_singleton(b):
        return a is b
    else:
        return a == b


def is_generator(x):
    """Check if an object is a generator expression or generator function.

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is a generator, False otherwise.

    Examples:
        >>> def _gen(): yield 1
        >>> is_generator(_gen)
        True
        >>> is_generator(i for i in range(5))
        True
        >>> is_generator(None)
        False
        >>> is_generator(1)
        False
    """
    return is_generator_expression(x) or is_generator_function(x)


def is_generator_expression(x):
    """Check if an object is a generator expression.

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is a generator expression, False otherwise.

    Examples:
        >>> is_generator_expression(i for i in range(5))
        True
        >>> def _gen(): yield 1
        >>> is_generator_expression(_gen)
        False
        >>> is_generator_expression(None)
        False
        >>> is_generator_expression(1)
        False
    """
    return inspect.isgenerator(x)


def is_generator_function(x):
    """Check if an object is a generator function.

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is a generator function, False otherwise.

    Examples:
        >>> def _gen(): yield 1
        >>> is_generator_function(_gen)
        True
        >>> is_generator_function(i for i in range(5))
        False
        >>> is_generator_function(None)
        False
        >>> is_generator_function(1)
        False
    """
    return inspect.isgeneratorfunction(x)


def is_iterable(x):
    """Check if an object is iterable.

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is iterable, False otherwise.

    Examples:
        >>> is_iterable([1,2,3])
        True
        >>> is_iterable(map(float, range(5)))
        True
        >>> is_iterable(None)
        False
        >>> is_iterable(1)
        False
        >>> is_iterable('hello')
        False
    """
    if is_generator(x):
        return True

    try:
        # The only reliable way to determine whether an object is iterable is to call iter(obj).
        iter(x)
        # str, bytes, bytearray are theoretically a iterables,
        # but in practice we use them as primitives
        return not isinstance(x, (str, bytes, bytearray))
    except TypeError:
        return False


def is_iterable_or_str(x):
    """Check if an object is iterable or a string.

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is iterable or a string, False otherwise.

    Examples:
        >>> is_iterable_or_str([1,2,3])
        True
        >>> is_iterable_or_str('hello')
        True
        >>> is_iterable_or_str(map(float, range(5)))
        True
        >>> is_iterable_or_str(None)
        False
        >>> is_iterable_or_str(1)
        False
    """
    return is_generator(x) or isinstance(x, collections.abc.Iterable)


def is_iterator(x):
    """Check if an object is an iterator.

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is an iterator, False otherwise.

    Examples:
        >>> is_iterator(iter([]))
        True
        >>> is_iterator(iter({1,2,3}))
        True
        >>> is_iterator(map(float, range(5)))
        True
        >>> is_iterator(None)
        False
        >>> is_iterator([])
        False
    """
    return is_generator(x) or isinstance(x, collections.abc.Iterator)


def is_none_of(needle, haystack):
    """Check if the needle is not in the haystack. This correctly compares singletons
    (None, True, False) using `is` and other values using `==`.

    Args:
        needle (Any): The value to compare against the elements in the haystack.
        haystack (Iterable): The iterable containing the elements to compare with the needle.

    Returns:
        bool: True if the needle is not equal to any element in the haystack, False otherwise.

    Examples:
        >>> is_none_of(1, [])
        True
        >>> is_none_of(2, [1, 3])
        True
        >>> is_none_of(1, [1])
        False
        >>> is_none_of([1, 2], [[1, 2], 3, 4])
        False
    """
    return not is_any_of(needle, haystack)


def is_number(x):
    """Check if an object is a number (int, float, complex, Decimal, Fraction).

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is a number, False otherwise.

    Examples:
        >>> is_number(1)
        True
        >>> is_number(Decimal('3.14'))
        True
        >>> is_number(-0.1)
        True
        >>> is_number(None)
        False
        >>> is_number([])
        False
    """
    if isinstance(x, bool):
        return None

    return isinstance(x, (int, float, complex, Decimal, Fraction))


def is_pathlike(obj):
    return isinstance(obj, (str, os.PathLike))


def is_primitive(x):
    """Check if an object is a primitive. Return True for str because in practice we use
    it as a primitive, even though it is theoretically a collection.

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is a primitive, False otherwise.

    Examples:
        >>> is_primitive(1)
        True
        >>> is_primitive('hello')
        True
        >>> is_primitive(False)
        True
        >>> is_primitive([])
        False
    """
    return isinstance(x, (str, int, float, bool, type(None), bytes, bytearray))


def is_sequence(x):
    """Check if an object is a sequence. This function excludes str, bytes, and
    bytearray from being considered sequences, although because in practice they are
    used as primitives.

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is a sequence, False otherwise.

    Examples:
        >>> is_sequence([1, 2, 3])
        True
        >>> is_sequence('hello')
        False
        >>> is_sequence(0)
        False
        >>> is_sequence({1, 2, 3})
        False
        >>> is_sequence({'a': 1})
        False
    """
    return isinstance(x, collections.abc.Sequence) and not isinstance(x, (str, bytes, bytearray))


def is_sequence_of_dicts(x, *, empty_ok=True):
    """Check if an object is a sequence of dictionaries.

    Args:
        x (Any): The object to check.
        empty_ok (bool, optional): Specifies whether an empty sequence is allowed. Defaults to True.

    Returns:
        bool: True if the object is a sequence of dictionaries, False otherwise.

    Examples:
        >>> is_sequence_of_dicts([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])
        True
        >>> is_sequence_of_dicts([{}, {}])
        True
        >>> is_sequence_of_dicts([{'a': 1, 'b': 2}, {'a': 3, 'b': 4, 'c': 5}])
        True
        >>> is_sequence_of_dicts([], empty_ok=False)
        False
        >>> is_sequence_of_dicts([], empty_ok=True)
        True
    """
    if not isinstance(empty_ok, bool):
        raise TypeError(f"<empty_ok> expects False or True. Got {type(empty_ok)}")

    if is_sequence(x):
        if (len(x) >= 1 and all(isinstance(xi, dict) for xi in x)) or (len(x) == 0 and empty_ok):
            return True

    return False


def is_sequence_of_dicts_uniform(x, *, empty_ok=True):
    """Check if x is a sequence of dictionaries and all dicts have the same keys.

    Args:
        x (Any): The sequence of dictionaries to check.
        empty_ok (bool, optional): Specifies whether an empty sequence is allowed. Defaults to True.

    Returns:
        bool: True if the object is a sequence of dictionaries and they have the same keys, False otherwise.

    Examples:
        >>> is_sequence_of_dicts_uniform([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])
        True
        >>> is_sequence_of_dicts_uniform([{}, {}])
        True
        >>> is_sequence_of_dicts_uniform([{'a': 1, 'b': 2}, {'a': 3, 'b': 4, 'c': 5}])
        False
        >>> is_sequence_of_dicts_uniform([], empty_ok=False)
        False
        >>> is_sequence_of_dicts_uniform([], empty_ok=True)
        True
    """
    if not is_sequence_of_dicts(x, empty_ok=empty_ok):
        return False
    elif len(x) == 0 and empty_ok:
        return True

    keys = set(x[0].keys())
    return all(set(xi.keys()) == keys for xi in x)


def is_sequence_of_sequences(x, *, empty_ok=True):
    """Check if an object is a sequence of sequences.

    Args:
        x (Any): The object to check.
        empty_ok (bool, optional): Specifies whether an empty sequence is allowed. Defaults to True.

    Returns:
        bool: True if the object is a sequence of sequences, False otherwise.

    Examples:
        >>> is_sequence_of_sequences([[1, 2], [3, 4]])
        True
        >>> is_sequence_of_sequences([[], []])
        True
        >>> is_sequence_of_sequences([[1, 2], [3]])
        True
        >>> is_sequence_of_sequences([], empty_ok=False)
        False
        >>> is_sequence_of_sequences([], empty_ok=True)
        True
    """
    if not isinstance(empty_ok, bool):
        raise TypeError(f"<empty_ok> expects False or True. Got {type(empty_ok)}")

    if is_sequence(x):
        if (len(x) >= 1 and all(is_sequence(xi) for xi in x)) or (len(x) == 0 and empty_ok):
            return True

    return False


def is_sequence_of_sequences_uniform(x, *, empty_ok=True):
    """Check if x is a sequence of sequences and all sequences have the same length.

    Args:
        x (Any): The sequence of sequences to check.
        empty_ok (bool, optional): Specifies whether an empty sequence is allowed. Defaults to True.

    Returns:
        bool: True if the object is a sequence of sequences and they have the same length, False otherwise.

    Examples:
        >>> is_sequence_of_sequences_uniform([[1, 2], [3, 4]])
        True
        >>> is_sequence_of_sequences_uniform([[], []])
        True
        >>> is_sequence_of_sequences_uniform([[1, 2], [3]])
        False
        >>> is_sequence_of_sequences_uniform([], empty_ok=False)
        False
        >>> is_sequence_of_sequences_uniform([], empty_ok=True)
        True
    """
    if not is_sequence_of_sequences(x, empty_ok=empty_ok):
        return False
    elif len(x) == 0 and empty_ok:
        return True

    n = len(x[0])
    return all(len(xi) == n for xi in x)


def is_sequence_or_str(x):
    """Check if an object is a sequence or a string.

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is a sequence or a string, False otherwise.

    Examples:
        >>> is_sequence_or_str([1, 2, 3])
        True
        >>> is_sequence_or_str('hello')
        True
        >>> is_sequence_or_str(0)
        False
        >>> is_sequence_or_str({1, 2, 3})
        False
        >>> is_sequence_or_str({'a': 1})
        False
    """
    return isinstance(x, collections.abc.Sequence)


def is_singleton(x):
    """Check if an object is a singleton (True, False, or None).

    Args:
        x (Any): The object to check.

    Returns:
        bool: True if the object is a singleton, False otherwise.

    Examples:
        >>> is_singleton(True)
        True
        >>> is_singleton(None)
        True
        >>> is_singleton([None])
        False
        >>> is_singleton({'a': 1})
        False
    """
    return isinstance(x, (bool, type(None)))


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
