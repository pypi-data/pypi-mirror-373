# """This module contains various utility functions for extracting and transforming data.

# Examples:
#     >>> first([1, 6, 2], condition=lambda x: x % 2 == 0)
#     6

#     >>> detect_fronts_positive('00101101')
#     [2, 4, 7]

#     >>> swap_keys_and_values({'a': 1, 'b': 2, 'c': 3})
#     {1: 'a', 2: 'b', 3: 'c'}

#     >>> as_dict_of_lists([['a', 'b'], [1, 2], [3, 4]])
#     {'a': [1, 3], 'b': [2, 4]}
# """

import copy

from katalytic._pkg import _UNDEFINED
from katalytic.data.checks import (
    is_any_of,
    is_dict_of_sequences_uniform,
    is_iterable,
    is_iterator,
    is_none_of,
    is_primitive,
    is_sequence,
    is_sequence_of_dicts_uniform,
    is_sequence_of_sequences_uniform,
)


def as_dict_of_lists(data, *, empty_ok=True):
    """Convert data into a dictionary of lists format.

    This format is useful when you need to perform operations on each column
    of a table. It provides a compact representation of the data, but may be less intuitive.

    Args:
        data (Union[Sequence[Dict], Sequence[Sequence], Dict]): The input data to convert.
        empty_ok (bool): Whether to allow an empty collection. Defaults to True.

    Returns:
        Dict: The data in dictionary of lists format.

    Raises:
        TypeError: If the input data has an unexpected format.

    Examples:
        >>> as_dict_of_lists({'b': [3, 4], 'a': [1, 2]})
        {'b': [3, 4], 'a': [1, 2]}

        >>> as_dict_of_lists(({'a': 1, 'b': 2}, {'b': 4, 'a': 3}))
        {'a': [1, 3], 'b': [2, 4]}

        >>> as_dict_of_lists([['b', 'a'], [1, 2], [3, 4]])
        {'b': [1, 3], 'a': [2, 4]}
    """
    if not isinstance(empty_ok, bool):
        raise TypeError(f"<empty_ok> expects False or True. Got {type(empty_ok)}")

    if (isinstance(data, dict) or is_sequence(data)) and len(data) == 0:
        if empty_ok:
            return []
        else:
            raise ValueError("Empty collection not allowed when <empty_ok> is False")
    elif is_sequence_of_dicts_uniform(data):
        return {k: [d[k] for d in data] for k in data[0]}
    elif is_sequence_of_sequences_uniform(data):
        return {k: [v[i] for v in data[1:]] for i, k in enumerate(data[0])}
    elif is_dict_of_sequences_uniform(data):
        return {k: list(v) for k, v in data.items()}
    else:
        raise TypeError(f"Unexpected format for <data>. Got {type(data).__name__}: {data!r}")


def as_list_of_dicts(data, *, empty_ok=True):
    """Convert data into a list of dictionaries format.

    This format is useful when you need to perform operations on each row of a table.

    Args:
        data (Union[Sequence[Dict], Sequence[Sequence], Dict]): The input data to convert.
        empty_ok (bool): Whether to allow an empty collection. Defaults to True.

    Returns:
        List[Dict]: The data in list of dictionaries format.

    Raises:
        TypeError: If the input data has an unexpected format.

    Examples:
        >>> as_list_of_dicts({'a': [1, 2], 'b': [3, 4]})
        [{'a': 1, 'b': 3}, {'a': 2, 'b': 4}]

        >>> as_list_of_dicts([['b', 'a'], [1, 2], [3, 4]])
        [{'b': 1, 'a': 2}, {'b': 3, 'a': 4}]

        >>> as_list_of_dicts([{'b': 2, 'a': 1}, {'a': 3, 'b': 4}])
        [{'b': 2, 'a': 1}, {'b': 4, 'a': 3}]
    """
    if not isinstance(empty_ok, bool):
        raise TypeError(f"<empty_ok> expects False or True. Got {type(empty_ok)}")

    if (isinstance(data, dict) or is_sequence(data)) and len(data) == 0:
        if empty_ok:
            return []
        else:
            raise ValueError("Empty collection not allowed when <empty_ok> is False")
    elif is_sequence_of_dicts_uniform(data):
        header = list(data[0].keys())
        return [{k: d[k] for k in header} for d in data]
    elif is_sequence_of_sequences_uniform(data):
        return [dict(zip(data[0], row, strict=False)) for row in data[1:]]
    elif is_dict_of_sequences_uniform(data):
        first_seq = list(data.values())[0]
        seq_len = len(first_seq)
        return [{k: v[i] for k, v in data.items()} for i in range(seq_len)]
    else:
        raise TypeError(f"Unexpected format for <data>. Got {type(data).__name__}: {data!r}")


def as_list_of_lists(data, *, empty_ok=True):
    """Convert data into a list of lists format.

    This format, along with the dict_of_sequences format, is the most compact for storing tabular data.
    This format is more intuitive than the dict_of_sequences format.

    Args:
        data (Union[Sequence[Dict], Sequence[Sequence], Dict]): The input data to convert.
        empty_ok (bool): Whether to allow an empty collection. Defaults to True.

    Returns:
        List[List]: The data in list of lists format.

    Raises:
        TypeError: If the input data has an unexpected format.

    Examples:
        >>> as_list_of_lists({'a': [1, 2], 'b': [3, 4]})
        [['a', 'b'], [1, 3], [2, 4]]

        >>> as_list_of_lists(({'a': 1, 'b': 2}, {'a': 3, 'b': 4}))
        [['a', 'b'], [1, 2], [3, 4]]

        >>> as_list_of_lists([['b', 'a'], [1, 2], [3, 4]])
        [['b', 'a'], [1, 2], [3, 4]]
    """
    if not isinstance(empty_ok, bool):
        raise TypeError(f"<empty_ok> expects False or True. Got {type(empty_ok)}")

    if (isinstance(data, dict) or is_sequence(data)) and len(data) == 0:
        if empty_ok:
            return []
        else:
            raise ValueError("Empty collection not allowed when <empty_ok> is False")
    elif is_sequence_of_dicts_uniform(data):
        header = [list(data[0].keys())]
        rows = [[d[k] for k in header[0]] for d in data]
        return header + rows
    elif is_sequence_of_sequences_uniform(data):
        return list(map(list, data))
    elif is_dict_of_sequences_uniform(data):
        header = [list(data.keys())]
        n = len(list(data.values())[0])
        rows = [[v[i] for v in data.values()] for i in range(n)]
        return header + rows
    else:
        raise TypeError(f"Unexpected format for <data>. Got {type(data).__name__}: {data!r}")


def detect_runs(values):
    """Detects runs of equal values.

    Args:
        values (Iterable or str): A string or a list representing binary values.

    Returns:
        List[Tuple[int, int]]: The list of tuples representing the runs
            formatted as (index, change) where index is the index at which
            the bit flip takes place and change is 1 for positive runs
            and -1 for negative runs.

    Example:
        >>> detect_runs("00101101")
        [(0, 1, 2, '0'), (2, 2, 1, '1'), (3, 3, 1, '0'), (4, 5, 2, '1'), (6, 6, 1, '0'), (7, 7, 1, '1')]

        >>> detect_runs([0, 0, 1, 0, 1, 1, 0, 1])
        [(0, 1, 2, 0), (2, 2, 1, 1), (3, 3, 1, 0), (4, 5, 2, 1), (6, 6, 1, 0), (7, 7, 1, 1)]

        >>> detect_runs([False, False, True, False, True, True, False, True])
        [(0, 1, 2, False), (2, 2, 1, True), (3, 3, 1, False), (4, 5, 2, True), (6, 6, 1, False), (7, 7, 1, True)]

        >>> detect_runs(["hello", "hello", "world", 42, 42, 42])
        [(0, 1, 2, 'hello'), (2, 2, 1, 'world'), (3, 5, 3, 42)]
    """
    if not values:
        return []

    values = iter(values)
    runs = []

    current_start = 0
    current_value = next(values)
    for i, value in enumerate(values, start=1):
        if value != current_value:
            runs.append((current_start, i - 1, i - current_start, current_value))

            current_start = i
            current_value = value

    runs.append((current_start, i, i - current_start + 1, current_value))

    return runs


def detect_fronts(bits):
    """Detects the fronts in a sequence of bits.

    A front is a change from 0 to 1 (positive) or from 1 to 0 (negative).
    It works even if the bits are booleans instead of 0/1.

    Returns a list of tuples
    Args:
        bits (Iterable or str): A string or a list representing binary values.

    Returns:
        List[Tuple[int, int]]: The list of tuples representing the fronts
            formatted as (index, bit) where index is the index at which
            the bit flip takes place and bit is 1 for positive fronts
            and 0 for negative fronts.

    Raises:
        TypeError: If the bits are not of the expected types.

    Example:
        >>> bits = "00101101"
        >>> detect_fronts(bits)
        [(0, 0), (2, 1), (3, 0), (4, 1), (6, 0), (7, 1)]

        >>> bits = [0, 0, 1, 0, 1, 1, 0, 1]
        >>> detect_fronts(bits)
        [(0, 0), (2, 1), (3, 0), (4, 1), (6, 0), (7, 1)]

        >>> bits = [False, False, True, False, True, True, False, True]
        >>> detect_fronts(bits)
        [(0, 0), (2, 1), (3, 0), (4, 1), (6, 0), (7, 1)]
    """
    try:
        bits = [int(b.real) if isinstance(b, complex) else int(b) for b in bits]
    except Exception:
        raise ValueError(f"Only 0/1 or True/False are allowed. Got {bits!r}")

    if not all(b in (0, 1) for b in bits):
        raise ValueError(f"Only 0/1 or True/False are allowed. Got {bits!r}")

    if not bits:
        return []

    fronts = [(0, bits[0])]
    for i, (a, b) in enumerate(zip(bits, bits[1:], strict=False), start=1):
        if a != b:
            fronts.append((i, b))

    return fronts


def detect_fronts_positive(bits):
    """Detects the positive fronts (a 0 to 1 transition).

    Args:
        bits (str or list): A string or a list representing binary values.

    Returns:
        list: A list of indices at which the bit flip from 0 to 1 occurs.

    Example:
        >>> detect_fronts_positive("00101101")
        [2, 4, 7]

        >>> detect_fronts_positive([0, 0, 1, 0, 1, 1, 0, 1])
        [2, 4, 7]

        >>> bits = [False, False, True, False, True, True, False, True]
        >>> detect_fronts_positive(bits)
        [2, 4, 7]
    """
    return [i for i, bit in detect_fronts(bits) if bit == 1]


def detect_fronts_negative(bits):
    """Detects the negative fronts (a 1 to 0 transition).

    Args:
        bits (str or list): A string or a list representing binary values.

    Returns:
        list: A list of indices at which the bit flip from 1 to 0 occurs.

    Example:
        >>> bits = "00101101"
        >>> detect_fronts_negative(bits)
        [0, 3, 6]

        >>> bits = [0, 0, 1, 0, 1, 1, 0, 1]
        >>> detect_fronts_negative(bits)
        [0, 3, 6]

        >>> bits = [False, False, True, False, True, True, False, True]
        >>> detect_fronts_negative(bits)
        [0, 3, 6]
    """
    return [i for i, bit in detect_fronts(bits) if bit == 0]


def first(data, *, condition=lambda _: True, default=_UNDEFINED):
    """Returns the first element from a sequence.

    Args:
        data (sequence): The sequence from which to retrieve the first element.
        condition (function, optional): A function to specify the condition for comparison. Defaults to lambda _: True.

    Returns:
        The first element from the sequence.

    Raises:
        TypeError: If data is a set. Use `one(data)` instead for sets.

    Example:
        >>> data = [1, 2, 3, 4, 5]
        >>> first(data)
        1

        >>> data = [1, 2, 3, 4, 5]
        >>> first(data, condition=lambda x: x % 2 == 0)
        2
    """
    if isinstance(data, set):
        raise TypeError("<data> expects a sequence. Got set. Use `one(data)` instead")

    return one(data, condition=condition, default=default)


def first_with_idx(data, *, condition=lambda _: True, default=_UNDEFINED):
    """Returns the first element and its index from a sequence.

    Args:
        data (sequence): The sequence to search in.
        condition (function, optional): A function to specify the condition for comparison. Defaults to lambda _: True.

    Returns:
        tuple or None: A tuple containing the index and the first element
            that satisfies the condition specified by the condition function.

            When no item is found, returns None instead of (None, None).
            (None, None) lets you use unpacking everywhere, but it's a bad idea because
            it's evaluated as truthy in `if first_with_idx(...): ...`
            It would lead to a lot of counter-intuitive bugs, so it's better to avoid it

    Raises:
        TypeError: If data is a set. Use `one(data)` instead for sets.
        TypeError: If condition is not a callable function.

    Example:
        >>> first_with_idx([1, 2, 3, 4, 5])
        (0, 1)
        >>> first_with_idx([10, 20, 30, 40, 50], condition=lambda x: x % 3 == 0)
        (2, 30)
        >>> first_with_idx([1, 3, 5], condition=lambda x: x % 2 == 0, default=None)
    """
    if isinstance(data, set):
        raise TypeError("<data> expects a sequence. Got set. Use `one(data)` instead")
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}: {condition!r}")

    for i, v in enumerate(data):
        if condition(v):
            return (i, v)

    return default


def flatten(iterable):
    """Flatten one level of the iterable.

    Args:
        iterable (Iterable): The iterable to flatten.

    Returns:
        list: An iterable flattened by one level.

    Raises:
        TypeError: If the input is not an iterable.

    Examples:
        >>>
    """
    if not is_iterable(iterable):
        raise TypeError(f"<iterable> expects an iterable. Got {type(iterable).__name__}")

    flat = []
    for x in iterable:
        if is_iterable(x):
            flat.extend(x)
        else:
            flat.append(x)

    return flat


def flatten_recursive(iterable):
    """Recursively flattens an iterable.

    Args:
        iterable (Iterable): The iterable to be flattened.

    Returns:
        list: The flattened list.

    Example:
        >>> iterable = [1, [2, [3, 4], 5], 6]
        >>> flatten_recursive(iterable)
        [1, 2, 3, 4, 5, 6]
    """
    new = flatten(iterable)
    if new == iterable:
        return new
    else:
        return flatten_recursive(new)


def last(data, *, condition=lambda _: True, default=_UNDEFINED):
    """Returns the last element from a sequence.

    Args:
        data (sequence): The sequence from which to retrieve the last element.
        condition (function, optional): A function to specify the condition for comparison. Defaults to lambda _: True.

    Returns:
        The last element from the sequence.

    Raises:
        TypeError: If data is a set. Use `one(data)` instead for sets.

    Example:
        >>> last([1, 2, 3, 4, 5])
        5

        >>> last([1, 2, 3, 4, 5], condition=lambda x: x % 2 == 0)
        4
    """
    if isinstance(data, set):
        raise TypeError("<data> expects a sequence. Got set. Use `one(data)` instead")

    if is_iterator(data) or isinstance(data, dict):
        data = list(data)

    return one(reversed(data), condition=condition, default=default)


def last_with_idx(data, *, condition=lambda _: True, default=_UNDEFINED):
    """Returns the last element and its index from a sequence.

    Args:
        data (sequence): The sequence to search in.
        condition (function, optional): A function to specify the condition for comparison. Defaults to lambda _: True.

    Returns:
        tuple or None: A tuple containing the index and the first element
            that satisfies the condition specified by the condition function.

            When no item is found, returns None instead of (None, None).
            (None, None) lets you use unpacking everywhere, but it's a bad idea because
            it's evaluated as truthy in `if first_with_idx(...): ...`
            It would lead to a lot of counter-intuitive bugs, so it's better to avoid it

    Raises:
        TypeError: If data is a set. Use `one(data)` instead for sets.
        TypeError: If condition is not a callable function.

    Example:
        >>> last_with_idx([1, 2, 3, 4, 5])
        (4, 5)
        >>> last_with_idx([1, 2, 3, 4, 5], condition=lambda x: x % 2 == 0)
        (3, 4)
        >>> last_with_idx([1, 3, 5], condition=lambda x: x % 2 == 0, default=None)
    """
    if isinstance(data, set):
        raise TypeError("<data> expects a sequence. Got set. Use `one(data)` instead")
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}: {condition!r}")

    if is_iterator(data) or isinstance(data, dict):
        data = list(data)

    for i, v in enumerate(reversed(data), start=1):
        if condition(v):
            return (len(data) - i, v)

    return default


def map_dict_keys(f, data, *, condition=None):
    """Maps the keys of a dictionary to new keys using a function.

    Args:
        f (function): The function to apply to each key.
        data (dict): The dictionary to map the keys of.
        condition (function, optional): A condition function to selectively apply the mapping. Defaults to None.

    Returns:
        dict: A new dictionary with the mapped keys.

    Raises:
        TypeError: If f is not a callable function.
        TypeError: If data is not a dictionary.
        TypeError: If condition is neither None nor a callable function.

    Example:
        >>> def square(x):
        ...     return x ** 2
        ...
        >>> data = {1: 'one', 2: 'two', 3: 'three'}
        >>> map_dict_keys(square, data)
        {1: 'one', 4: 'two', 9: 'three'}

        >>> def is_even(x):
        ...     return x % 2 == 0
        ...
        >>> data = {1: 'one', 2: 'two', 3: 'three'}
        >>> map_dict_keys(square, data, condition=is_even)
        {1: 'one', 4: 'two', 3: 'three'}
    """
    if not callable(f):
        raise TypeError(f"<f> expects a function. Got {type(f).__name__}: {f!r}")
    elif not isinstance(data, dict):
        raise TypeError(f"<data> expects a dict. Got {type(data).__name__}: {data!r}")
    elif not (condition is None or callable(condition)):
        raise TypeError(f"<condition> expects None or a function. Got {type(condition).__name__}: {condition!r}")

    if condition is None:
        return {f(k): v for k, v in data.items()}
    else:
        return {f(k) if condition(k) else k: v for k, v in data.items()}


def map_dict_values(f, data, *, condition=None):
    """Maps the values of a dictionary to new values using a function.

    Args:
        f (function): The function to apply to each value.
        data (dict): The dictionary to map the values of.
        condition (function, optional): A condition function to selectively apply the mapping. Defaults to None.

    Returns:
        dict: A new dictionary with the mapped values.

    Raises:
        TypeError: If f is not a callable function.
        TypeError: If data is not a dictionary.
        TypeError: If condition is neither None nor a callable function.

    Example:
        >>> def uppercase(s):
        ...     return s.upper()
        ...
        >>> data = {'a': 'apple', 'b': 'banana', 'c': 'cherry'}
        >>> map_dict_values(uppercase, data)
        {'a': 'APPLE', 'b': 'BANANA', 'c': 'CHERRY'}

        >>> def is_long(s):
        ...     return len(s) > 5
        ...
        >>> data = {'a': 'apple', 'b': 'banana', 'c': 'cherry'}
        >>> map_dict_values(uppercase, data, condition=is_long)
        {'a': 'apple', 'b': 'BANANA', 'c': 'CHERRY'}
    """
    if not callable(f):
        raise TypeError(f"<f> expects a function. Got {type(f).__name__}: {f!r}")
    elif not isinstance(data, dict):
        raise TypeError(f"<data> expects a dict. Got {type(data).__name__}: {data!r}")
    elif not (condition is None or callable(condition)):
        raise TypeError(f"<condition> expects None or a function. Got {type(condition).__name__}: {condition!r}")

    if condition is None:
        return {k: f(v) for k, v in data.items()}
    else:
        return {k: f(v) if condition(v) else v for k, v in data.items()}


def map_recursive(f, data, *, condition=is_primitive, on_dict_keys=False):
    """Recursively maps a function over elements in a data structure, based on specified
    conditions.

    Args:
        f: The function to be applied to the elements. Must be callable.
        data: The data structure to be mapped over. Must be iterable.
        condition (optional):
            A function to determine whether an element should be mapped or not. If None, all elements
            are mapped. Default is is_primitive, which maps only primitives (not containers). (default: is_primitive)
        on_dict_keys (optional):
            Specifies whether to apply the mapping on dictionary keys.
            If True, the function will also be applied to dictionary keys. Default is False. (default: False)

    Returns:
        The data structure with the mapped elements.

    Raises:
        TypeError: If f is not callable, data is not iterable, condition is not None or callable,
         or on_dict_keys is not a boolean.

    Examples:
        1. Mapping a function over a list:
            >>> data = [1, 2, 3]
            >>> def square(x):
            ...     return x ** 2
            >>> map_recursive(square, data)
            [1, 4, 9]

        2. Mapping a function over a nested dictionary:
            >>> data = {'a': [1, 2, 3], 'b': {'c': [4, 5, 6]}}
            >>> def double(x):
            ...     return 2 * x
            >>> map_recursive(double, data)
            {'a': [2, 4, 6], 'b': {'c': [8, 10, 12]}}
    """
    if not callable(f):
        raise TypeError(f"<f> expects a function. Got {type(f).__name__}: {f!r}")
    elif not is_iterable(data):
        raise TypeError(f"<data> expects an iterable. Got {type(data).__name__}: {data!r}")
    elif not (condition is None or callable(condition)):
        raise TypeError(f"<condition> expects None or a function. Got {type(condition).__name__}: {condition!r}")
    elif not isinstance(on_dict_keys, bool):
        raise TypeError(f"<on_dict_keys> expects True or False. Got {type(on_dict_keys).__name__}: {on_dict_keys!r}")

    if is_iterator(data):
        new_data = (
            (
                map_recursive(f, v, condition=condition, on_dict_keys=on_dict_keys)
                if is_iterable(v)
                else f(v) if condition(v) else v
            )
            for v in data
        )
    elif isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if on_dict_keys:
                if is_iterable(k):
                    k = map_recursive(f, k, condition=condition, on_dict_keys=on_dict_keys)
                if condition(k):
                    k = f(k)

            if is_iterable(v):
                v = map_recursive(f, v, condition=condition, on_dict_keys=on_dict_keys)
            if condition(v):
                v = f(v)

            new_data[k] = v
    else:
        new_data = type(data)(
            (
                map_recursive(f, v, condition=condition, on_dict_keys=on_dict_keys)
                if is_iterable(v)
                else f(v) if condition(v) else v
            )
            for v in data
        )

    if condition(new_data):
        return f(new_data)
    else:
        return new_data


def one(data, *, condition=lambda _: True, default=_UNDEFINED):
    """Returns an element from an iterable that satisfies a given condition specified by the condition function.

    Args:
        data (iterable): The iterable to search in.
        condition (function, optional): A function to specify the condition. Defaults to lambda _: True.

    Returns:
        Any or None: An element that satisfies the condition. Returns None if no such element is found.

    Raises:
        TypeError: If condition is not a callable function.
        TypeError: If data is not an iterable.

    Example:
        >>> data = [1, 2, 3, 4, 5]
        >>> one(data)
        1

        >>> data = [1, 2, 3, 4, 5]
        >>> one(data, condition=lambda x: x % 2 == 0)
        2

        >>> data = [1, 3, 5]
        >>> one(data, condition=lambda x: x % 2 == 0, default=None)
    """
    if not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}: {condition!r}")
    elif not is_iterable(data):
        raise TypeError(f"<data> expects an iterable. Got {type(data).__name__}: {data!r}")

    return next(filter(condition, data), default)


def pop_min(data, *, condition=lambda x: x, default=_UNDEFINED):
    """Removes and returns the minimum element from the collection.

    If <condition> is specified, it will be used to determine the minimum element

    Args:
        data: The collection from which the minimum element is to be removed. Must be iterable.
        condition (optional):
            A function to sort by. The min is determined by applying the function to each element.
            By default it uses the identity function. (default: lambda x: x)
        default (optional):
            A default value to return for empty collections. If not provided and the collection is empty,
            a ValueError is raised. (default: _UNDEFINED)

    Returns:
        A tuple containing the minimum element and the modified collection without the minimum element.

    Raises:
        TypeError: If data is not iterable, data is a dict, or condition is not callable.
        ValueError: If the collection is empty and a default value is not provided.

    Note:
        For dictionaries, use `pop_min_key` or `pop_min_value` instead.

    Examples:
        1. Pop the minimum element from a list:
            >>> data = [3, 1, 4, 1, 5, 9]
            >>> pop_min(data)
            (1, [3, 4, 1, 5, 9])

        2. Pop the minimum element from a list using a condition function:
            >>> data = ['apple', 'banana', 'cherry']
            >>> pop_min(data, condition=len)
            ('apple', ['banana', 'cherry'])
    """
    if not is_iterable(data):
        raise TypeError(f"<data> expects an iterable. Got {type(data).__name__}: {data!r}")
    elif isinstance(data, dict):
        raise TypeError(
            "<data> expects any iterable besides dict. For dict, use `pop_min_key` or `pop_min_value` instead"
        )
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}: {condition!r}")

    original_type = type(data)
    data = [copy.deepcopy(item) for item in data]
    found = min(data, key=condition, default=_UNDEFINED)
    if found is _UNDEFINED and default is _UNDEFINED:
        raise ValueError("Cannot pop from an empty collection unless a default value is provided")

    data.remove(found)
    if original_type in (list, tuple, set, frozenset):
        return found, original_type(data)
    else:
        return found, data


def pop_max(data, *, condition=lambda x: x, default=_UNDEFINED):
    """Removes and returns the maximum element from the collection.

    If <condition> is specified, it will be used to determine the maximum element

    Args:
        data: The collection from which the maximum element is to be removed. Must be iterable.
        condition (optional):
            A function to sort by. The max is determined by applying the function to each element.
            By default it uses the identity function. (default: lambda x: x)
        default (optional):
            A default value to return for empty collections. If not provided and the collection is empty,
            a ValueError is raised. (default: _UNDEFINED)

    Returns:
        A tuple containing the maximum element and the modified collection without the maximum element.

    Raises:
        TypeError: If data is not iterable, data is a dict, or condition is not callable.
        ValueError: If the collection is empty and a default value is not provided.

    Note:
        For dictionaries, use `pop_max_key` or `pop_max_value` instead.

    Examples:
        1. Pop the maximum element from a list:
            >>> data = [3, 1, 4, 1, 5, 9]
            >>> pop_max(data)
            (9, [3, 1, 4, 1, 5])

        2. Pop the maximum element from a list using a condition function:
            >>> data = ['apple', 'banana', 'cherry']
            >>> pop_max(data, condition=len)
            ('banana', ['apple', 'cherry'])
    """
    if not is_iterable(data):
        raise TypeError(f"<data> expects an iterable. Got {type(data).__name__}: {data!r}")
    elif isinstance(data, dict):
        raise TypeError(
            "<data> expects any iterable besides dict. For dict, use `pop_max_key` or `pop_max_value` instead"
        )
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}: {condition!r}")

    original_type = type(data)
    data = [copy.deepcopy(item) for item in data]
    found = max(data, key=condition, default=_UNDEFINED)
    if found is _UNDEFINED and default is _UNDEFINED:
        raise ValueError("Cannot pop from an empty collection unless a default value is provided")

    data.remove(found)
    if original_type in (list, tuple, set, frozenset):
        return found, original_type(data)
    else:
        return found, data


def pop_max_by_dict_key(data, *, condition=lambda x: x, default=_UNDEFINED):
    """Removes and returns the maximum (key, value) pair from the dictionary based on
    the dictionary key.

    If the <condition> argument is specified, it will be used to calculate the maximum.

    Args:
        data: The dictionary from which the maximum (key, value) pair is to be removed. Must be a dict.
        condition (optional):
            A function to sort by. The max (key, value) pair is determined by applying the function to each dict key.
            By default it uses the identity function. (default: lambda x: x)
        default (optional):
            A default value to return for empty collections. If not provided and the collection is empty,
            a ValueError is raised. (default: _UNDEFINED)

    Returns:
        A tuple containing the maximum (key, value) pair and the modified dictionary without the pair.

    Raises:
        TypeError: If data is not a dict or condition is not callable.
        ValueError: If the dictionary is empty and a default value is not provided.

    Examples:
        1. Pop the maximum (key, value) pair from a dictionary:
            >>> data = {'a': 1, 'b': 2, 'c': 3}
            >>> pop_max_by_dict_key(data)
            (('c', 3), {'a': 1, 'b': 2})

        2. Pop the maximum (key, value) pair from a dictionary using a condition function:
            >>> data = {'apple': 3, 'banana': 2, 'cherry': 5}
            >>> pop_max_by_dict_key(data, condition=len)
            (('banana', 2), {'apple': 3, 'cherry': 5})
    """
    if not isinstance(data, dict):
        raise TypeError(f"<data> expects a dict. Got {type(data).__name__}: {data!r}")
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}: {condition!r}")

    data = copy.deepcopy(data)
    dict_key = max(data.keys(), key=condition, default=_UNDEFINED)
    if dict_key is _UNDEFINED and default is _UNDEFINED:
        raise ValueError("Cannot pop from an empty dict unless a default value is provided")

    value = data.pop(dict_key)
    return (dict_key, value), data


def pop_min_by_dict_key(data, *, condition=lambda x: x, default=_UNDEFINED):
    """Removes and returns the minimum (key, value) pair from the dictionary based on
    the dictionary key.

    If <condition> is specified, it will be used to calculate the minimum.

    Args:
        data: The dictionary from which the minimum (key, value) pair is to be removed. Must be a dict.
        condition (optional):
            A function to sort by. The min (key, value) pair is determined by applying the function to each dict key.
            By default it uses the identity function. (default: lambda x: x)
        default (optional):
            A default value to return for empty collections. If not provided and the collection is empty,
            a ValueError is raised. (default: _UNDEFINED)

    Returns:
        A tuple containing the minimum (key, value) pair and the modified dictionary without the pair.

    Raises:
        TypeError: If data is not a dict or condition is not callable.
        ValueError: If the dictionary is empty and a default value is not provided.

    Examples:
        1. Pop the minimum (key, value) pair from a dictionary:
            >>> data = {'a': 1, 'b': 2, 'c': 3}
            >>> pop_min_by_dict_key(data)
            (('a', 1), {'b': 2, 'c': 3})

        2. Pop the minimum (key, value) pair from a dictionary using a condition function:
            >>> data = {'apple': 3, 'banana': 2, 'cherry': 5}
            >>> pop_min_by_dict_key(data, condition=len)
            (('apple', 3), {'banana': 2, 'cherry': 5})
    """
    if not isinstance(data, dict):
        raise TypeError(f"<data> expects a dict. Got {type(data).__name__}: {data!r}")
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}: {condition!r}")

    data = copy.deepcopy(data)
    dict_key = min(data.keys(), key=condition, default=_UNDEFINED)
    if dict_key is _UNDEFINED and default is _UNDEFINED:
        raise ValueError("Cannot pop from an empty dict unless a default value is provided")

    value = data.pop(dict_key)
    return (dict_key, value), data


def pop_max_by_dict_value(data, *, condition=lambda x: x, default=_UNDEFINED):
    """Removes and returns the maximum (key, value) pair from the dictionary based on
    the dictionary value.

    If <condition> is specified, it will be used to calculate the maximum.

    Args:
        data: The dictionary from which the maximum (key, value) pair is to be removed. Must be a dict.
        condition (optional):
            A function to sort by. The max (key, value) pair is determined by applying the function to each dict value.
            By default it uses the identity function. (default: lambda x: x)
        default (optional):
            A default value to return for empty collections. If not provided and the collection is empty,
            a ValueError is raised. (default: _UNDEFINED)

    Returns:
        A tuple containing the maximum (key, value) pair and the modified dictionary without the pair.

    Raises:
        TypeError: If data is not a dict or condition is not callable.
        ValueError: If the dictionary is empty and a default value is not provided.

    Examples:
        >>> data = {'a': 1, 'b': 2, 'c': 3}
        >>> pop_max_by_dict_value(data)
        (('c', 3), {'a': 1, 'b': 2})
    """
    if not isinstance(data, dict):
        raise TypeError(f"<data> expects a dict. Got {type(data).__name__}: {data!r}")
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}: {condition!r}")

    data = copy.deepcopy(data)
    item = max(data.items(), key=lambda kv: condition(kv[1]), default=_UNDEFINED)
    if item is _UNDEFINED and default is _UNDEFINED:
        raise ValueError("Cannot pop from an empty dict unless a default value is provided")

    _ = data.pop(item[0])
    return item, data


def pop_min_by_dict_value(data, *, condition=lambda x: x, default=_UNDEFINED):
    """Removes and returns the minimum (key, value) pair from the dictionary based on
    the dictionary value.

    If <condition> is specified, it will be used to calculate the minimum.

    Args:
        data: The dictionary from which the minimum (key, value) pair is to be removed. Must be a dict.
        condition (optional):
            A function to sort by. The min (key, value) pair is determined by applying the function to each dict value.
            By default it uses the identity function. (default: lambda x: x)
        default (optional):
            A default value to return for empty collections. If not provided and the collection is empty,
            a ValueError is raised. (default: _UNDEFINED)

    Returns:
        A tuple containing the minimum (key, value) pair and the modified dictionary without the pair.

    Raises:
        TypeError: If data is not a dict or condition is not callable.
        ValueError: If the dictionary is empty and a default value is not provided.

    Examples:
        >>> data = {'a': 1, 'b': 2, 'c': 3}
        >>> pop_min_by_dict_value(data)
        (('a', 1), {'b': 2, 'c': 3})
    """
    if not isinstance(data, dict):
        raise TypeError(f"<data> expects a dict. Got {type(data).__name__}: {data!r}")
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}: {condition!r}")

    data = copy.deepcopy(data)
    item = min(data.items(), key=lambda kv: condition(kv[1]), default=_UNDEFINED)
    if item is _UNDEFINED and default is _UNDEFINED:
        raise ValueError("Cannot pop from an empty dict unless a default value is provided")

    _ = data.pop(item[0])
    return item, data


def pick_all(needles, haystack):
    """Returns a list of elements from the haystack that match any of the given needles.

    Args:
        needles: The elements to search for in the haystack. Must be iterable.
        haystack: The collection to search within. Must be iterable.

    Returns:
        A list of elements from the haystack that match any of the needles.

    Raises:
        TypeError: If needles or haystack is not iterable.

    Examples:
        >>> needles = [2, 4, 6]
        >>> haystack = [1, 2, 3, 4, 5, 6]
        >>> pick_all(needles, haystack)
        [2, 4, 6]
    """
    if not is_iterable(needles):
        raise TypeError(f"<needles> expects an iterable. Got {type(needles).__name__}: {needles!r}")
    elif not is_iterable(haystack):
        raise TypeError(f"<haystack> expects an iterable. Got {type(haystack).__name__}: {haystack!r}")

    return [needle for needle in needles if is_any_of(needle, haystack)]


def pick_all_besides(needles, haystack):
    """Returns a list of elements from the needles that are not present in the haystack.

    Args:
        needles: The elements to search for in the haystack. Must be iterable.
        haystack: The collection to search within. Must be iterable.

    Returns:
        A list of elements from the needles that are not present in the haystack.

    Raises:
        TypeError: If needles or haystack is not iterable.

    Examples:
        >>> needles = [2, 4, 6, 7]
        >>> haystack = [1, 2, 3, 4, 5]
        >>> pick_all_besides(needles, haystack)
        [6, 7]
    """
    if not is_iterable(needles):
        raise TypeError(f"<needles> expects an iterable. Got {type(needles).__name__}: {needles!r}")
    elif not is_iterable(haystack):
        raise TypeError(f"<haystack> expects an iterable. Got {type(haystack).__name__}: {haystack!r}")

    return [needle for needle in needles if is_none_of(needle, haystack)]


def pick_any(needles, haystack):
    """Returns the first element from the needles that is present in the haystack.

    Args:
        needles: The elements to search for in the haystack. Must be iterable.
        haystack: The collection to search within. Must be iterable.

    Returns:
        The first element from the needles that is present in the haystack, or None if no matching element is found.

    Raises:
        TypeError: If needles or haystack is not iterable.

    Examples:
        >>> needles = [2, 4, 6]
        >>> haystack = [1, 2, 3, 4, 5, 6]
        >>> pick_any(needles, haystack)
        2
    """
    if not is_iterable(needles):
        raise TypeError(f"<needles> expects an iterable. Got {type(needles).__name__}: {needles!r}")
    elif not is_iterable(haystack):
        raise TypeError(f"<haystack> expects an iterable. Got {type(haystack).__name__}: {haystack!r}")

    for needle in needles:
        if is_any_of(needle, haystack):
            return needle

    return None


def sort_dict_by_keys(data, *, condition=None, reverse=False):
    """Sorts a dictionary by its keys and returns a new dictionary.

    Args:
        data: The dictionary to be sorted. Must be a dict.
        condition (optional):
            A function to sort by. The keys are sorted based on the result of applying this function to each key.
            If None, the keys are sorted naturally. (default: None)
        reverse (optional):
            Reverses the sorting order. Sort in descending order if True and ascending otherwise. (default: False)

    Returns:
        A new dictionary sorted by keys.

    Raises:
        TypeError: If data is not a dict, condition is not callable or None, or reverse is not a boolean.

    Examples:
        >>> data = {'b': 2, 'a': 1, 'c': 3}
        >>> sort_dict_by_keys(data)
        {'a': 1, 'b': 2, 'c': 3}
    """
    if not isinstance(data, dict):
        raise TypeError(f"<data> expects a dict. Got {type(data).__name__}: {data!r}")
    elif not (condition is None or callable(condition)):
        raise TypeError(f"<condition> expects None or a function. Got {type(condition).__name__}: {condition!r}")
    elif not isinstance(reverse, bool):
        raise TypeError(f"<reverse> expects True or False. Got {type(reverse).__name__}: {reverse!r}")

    if condition is None:
        return dict(sorted(data.items(), reverse=reverse))
    else:
        return dict(sorted(data.items(), key=lambda kv: condition(kv[0]), reverse=reverse))


def sort_dict_by_keys_recursive(data, *, condition=None, reverse=False):
    """Recursively sorts a dictionary and its nested containers by their keys and
    returns a new structure.

    Args:
        data: The data structure to be sorted. Must be an iterable.
        condition (optional):
            A function to sort by. The keys are sorted based on the result of applying this function to each key.
            If None, the keys are sorted naturally. (default: None)
        reverse (optional):
            Reverses the sorting order. Sort in descending order if True and ascending otherwise. (default: False)

    Returns:
        A new structure with the nested dictionaries and containers sorted by keys.

    Raises:
        TypeError: If data is not an iterable, condition is not callable or None, or reverse is not a boolean.

    Examples:
        >>> data = {'b': {'c': 30, 'b': 20, 'a': 10}, 'a': {'c': 3, 'b': 2, 'a': 1}}
        >>> sort_dict_by_keys_recursive(data)
        {'a': {'a': 1, 'b': 2, 'c': 3}, 'b': {'a': 10, 'b': 20, 'c': 30}}
    """
    if not is_iterable(data):
        raise TypeError(f"<data> expects an iterable. Got {type(data).__name__}: {data!r}")
    elif not (condition is None or callable(condition)):
        raise TypeError(f"<condition> expects None or a function. Got {type(condition).__name__}: {condition!r}")
    elif not isinstance(reverse, bool):
        raise TypeError(f"<reverse> expects True or False. Got {type(reverse).__name__}: {reverse!r}")

    if isinstance(data, dict):
        return sort_dict_by_keys(
            {
                k: (sort_dict_by_keys_recursive(v, condition=condition, reverse=reverse) if is_iterable(v) else v)
                for k, v in data.items()
            },
            condition=condition,
            reverse=reverse,
        )
    elif is_iterator(data):
        return (
            (sort_dict_by_keys_recursive(v, condition=condition, reverse=reverse) if is_iterable(v) else v)
            for v in data
        )
    elif is_iterable(data):
        return type(data)(
            (sort_dict_by_keys_recursive(v, condition=condition, reverse=reverse) if is_iterable(v) else v)
            for v in data
        )


def sort_dict_by_values(data, *, condition=None, reverse=False):
    """Sorts a dictionary by its values and returns a new dictionary.

    Args:
        data: The dictionary to be sorted. Must be a dict.
        condition (optional):
            A function to sort by. The keys are sorted based on the result of applying this function to each value.
            If None, the values are sorted naturally. (default: None)
        reverse (optional):
            Reverses the sorting order. Sort in descending order if True and ascending otherwise. (default: False)

    Returns:
        A new dictionary sorted by values.

    Raises:
        TypeError: If data is not a dict, condition is not callable or None, or reverse is not a boolean.

    Examples:
        >>> data = {'a': 3, 'b': 1, 'c': 2}
        >>> sort_dict_by_values(data)
        {'b': 1, 'c': 2, 'a': 3}
    """
    if not isinstance(data, dict):
        raise TypeError(f"<data> expects a dict. Got {type(data).__name__}: {data!r}")
    elif not (condition is None or callable(condition)):
        raise TypeError(f"<condition> expects None or a function. Got {type(condition).__name__}: {condition!r}")
    elif not isinstance(reverse, bool):
        raise TypeError(f"<reverse> expects True or False. Got {type(reverse).__name__}: {reverse!r}")

    if condition is None:
        return dict(sorted(data.items(), key=lambda kv: kv[1], reverse=reverse))
    else:
        return dict(sorted(data.items(), key=lambda kv: condition(kv[1]), reverse=reverse))


def sort_dict_by_values_recursive(data, *, condition=None, reverse=False):
    """Recursively sorts a dictionary and its nested containers by their values and
    returns a new structure.

    Args:
        data: The data structure to be sorted. Must be an iterable.
        condition (optional):
            A function to sort by. The keys are sorted based on the result of applying this function to each value.
            If None, the values are sorted naturally. (default: None)
        reverse (optional):
            Reverses the sorting order. Sort in descending order if True and ascending otherwise. (default: False)

    Returns:
        A new structure with the nested dictionaries and containers sorted by values.

    Raises:
        TypeError: If data is not an iterable, condition is not callable or None, or reverse is not a boolean.
    """
    if not is_iterable(data):
        raise TypeError(f"<data> expects an iterable. Got {type(data).__name__}: {data!r}")
    elif not (condition is None or callable(condition)):
        raise TypeError(f"<condition> expects None or a function. Got {type(condition).__name__}: {condition!r}")
    elif not isinstance(reverse, bool):
        raise TypeError(f"<reverse> expects True or False. Got {type(reverse).__name__}: {reverse!r}")

    if isinstance(data, dict):
        return sort_dict_by_values(
            {
                k: (sort_dict_by_values_recursive(v, condition=condition, reverse=reverse) if is_iterable(v) else v)
                for k, v in data.items()
            },
            condition=condition,
            reverse=reverse,
        )
    elif is_iterator(data):
        return (
            (sort_dict_by_values_recursive(v, condition=condition, reverse=reverse) if is_iterable(v) else v)
            for v in data
        )
    elif is_iterable(data):
        return type(data)(
            (sort_dict_by_values_recursive(v, condition=condition, reverse=reverse) if is_iterable(v) else v)
            for v in data
        )


def sort_recursive(
    data,
    *,
    condition=lambda x: x,
    reverse=False,
    sort_dicts_by="keys",
    sort_iters=True,
    sort_lists=True,
    sort_sets=True,
    sort_tuples=True,
):
    """Recursively sorts an iterable data structure with customizable sorting options.
    The collections are sorted from the innermost to the outermost one.

    Args:
        data: The data structure to be sorted. Must be an iterable.
        condition (optional):
            A function to sort by. Sort based on the result of applying this function to each element.
            By default it uses the identity function. (default: lambda x: x)
        reverse (optional):
            Reverses the sorting order. Sort in descending order if True and ascending otherwise. (default: False)
        sort_dicts_by (optional):
            Specifies how to sort dicts. Sort by 'keys' or 'values'. If None, don't sort dicts. (default: 'keys')
        sort_iters (optional):
            Enable sort for iterable types (e.g., generator, range). default: True)
        sort_lists (optional): Enable sort for lists.(default: True)
        sort_sets (optional): Enable sort for sets. (default: True)
        sort_tuples (optional): Enable sort for tuples. (default: True)

    Returns:
        A new sorted data structure with the same nested structure.

    Raises:
        TypeError: If data is not an iterable or condition is not callable.
        ValueError: If sort_dicts_by has an invalid value.

    Examples:
        >>> data = [{'c': 3, 'b': {'z': 3, 'x': 2, 'y': 1}, 'a': 1}]
        >>> sort_recursive(data)
        [{'a': 1, 'b': {'x': 2, 'y': 1, 'z': 3}, 'c': 3}]
    """
    if not is_iterable(data):
        raise TypeError(f"<data> expects an iterable. Got {type(data).__name__}")
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}")
    elif not isinstance(reverse, bool):
        raise TypeError(f"<reverse> expects True or False. Got {type(reverse).__name__}")
    elif is_none_of(sort_dicts_by, ("keys", "values", None)):
        raise ValueError(f'<sort_dicts_by> expects "keys", "values" or None. Got {sort_dicts_by!r}')
    elif not isinstance(sort_iters, bool):
        raise TypeError(f"<sort_iters> expects True or False. Got {type(sort_iters).__name__}")
    elif not isinstance(sort_lists, bool):
        raise TypeError(f"<sort_lists> expects True or False. Got {type(sort_lists).__name__}")
    elif not isinstance(sort_sets, bool):
        raise TypeError(f"<sort_sets> expects True or False. Got {type(sort_sets).__name__}")
    elif not isinstance(sort_tuples, bool):
        raise TypeError(f"<sort_tuples> expects True or False. Got {type(sort_tuples).__name__}")

    initial_type = type(data)
    kwargs = {
        "condition": condition,
        "reverse": reverse,
        "sort_dicts_by": sort_dicts_by,
        "sort_iters": sort_iters,
        "sort_lists": sort_lists,
        "sort_sets": sort_sets,
        "sort_tuples": sort_tuples,
    }

    if isinstance(data, dict):
        # You shouldn't sort the keys, even if they are tuple,
        # as they are likely to be used as IDs
        inner_sorted = {k: sort_recursive(v, **kwargs) if is_iterable(v) else v for k, v in data.items()}
        if sort_dicts_by == "keys":
            return sort_dict_by_keys(inner_sorted, condition=condition, reverse=reverse)
        elif sort_dicts_by == "values":
            return sort_dict_by_values(inner_sorted, condition=condition, reverse=reverse)
        else:
            return inner_sorted

    inner_sorted = (sort_recursive(v, **kwargs) if is_iterable(v) else v for v in data)
    if is_iterator(data) and not sort_iters:
        return inner_sorted
    elif isinstance(data, list) and not sort_lists:
        return list(inner_sorted)
    elif isinstance(data, set) and not sort_sets:
        return set(inner_sorted)
    elif isinstance(data, tuple) and not sort_tuples:
        return tuple(inner_sorted)
    elif is_iterator(data) or isinstance(data, (set, list, tuple)):
        data = sorted(inner_sorted, key=condition, reverse=reverse)
        if initial_type == tuple:
            return tuple(data)
        else:
            return data
    else:  # pragma: no cover
        raise AssertionError(f"Unexpected branch for <data> of type {type(data).__name__}")


def swap_keys_and_values(data):
    """Swaps the keys and values in a dictionary.

    Args:
        data: The dictionary to swap keys and values. Must be a dict.

    Returns:
        A new dictionary with keys and values swapped.

    Raises:
        TypeError: If data is not a dict.

    Examples:
        Swap keys and values in a dictionary:
            >>> swap_keys_and_values({'a': 1, 'b': 2, 'c': 3})
            {1: 'a', 2: 'b', 3: 'c'}
    """
    if not isinstance(data, dict):
        raise TypeError(f"<data> expects a dict. Got {type(data).__name__}")

    return {v: k for k, v in data.items()}


def xor(*values, condition=bool):
    """Performs an exclusive OR (XOR) operation on multiple values using a condition
    function.

    Args:
        *values: Multiple values to perform the XOR operation on. At least two values are required.
        condition (optional):
            A function to determine the truthiness of each value. (default: bool)

    Returns: The value satisfying the XOR condition or None if the condition is False.

    Raises:
        ValueError: If less than two values are provided.
        TypeError: If condition is not callable.

    Examples:
        1. Perform XOR operation on a list of integers:
            >>> xor(0, 1, 0, 1, 0)

            >>> xor(0, 0, 0, 1, 0)
            1

        2. Perform XOR operation on a list of strings using a condition function:
            >>> xor('hello', '', 'world', condition=len)

            >>> xor('', 'hello', '', condition=len)
            'hello'
    """
    if len(values) < 2:
        raise ValueError("<values> expects at least two values")
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}")

    v = None
    for value in values:
        if condition(value):
            if v is None:
                v = value
            else:
                return None

    return v


def xor_with_idx(*values, condition=bool):
    """Performs a XOR (exclusive OR) operation on multiple values using a condition
    function.

    Args:
        *values: Multiple values to perform the XOR operation on. At least two values are required.
        condition (optional):
            A function to determine the truthiness of each value. (default: bool)

    Returns: The (index, value) satisfying the XOR condition or None if the condition is False.

    Raises:
        ValueError: If less than two values are provided.
        TypeError: If condition is not callable.

    Examples:
        1. Perform XOR operation on a list of integers:
            >>> xor_with_idx(0, 1, 0, 1, 0)

            >>> xor_with_idx(0, 0, 0, 1, 0)
            (3, 1)

        2. Perform XOR operation on a list of strings using a condition function:
            >>> xor_with_idx('hello', '', 'world', condition=len)

            >>> xor_with_idx('', 'hello', '', condition=len)
            (1, 'hello')
    """
    if len(values) < 2:
        raise ValueError("<values> expects at least two values")
    elif not callable(condition):
        raise TypeError(f"<condition> expects a function. Got {type(condition).__name__}")

    v = None
    for i, value in enumerate(values):
        if condition(value):
            if v is None:
                v = (i, value)
            else:
                return None

    return v


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
