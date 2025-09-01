from decimal import Decimal
from fractions import Fraction
from pathlib import Path, PosixPath

import pytest

from katalytic._pkg import (
    _C,
    _UNDEFINED,
    _C_obj,
    _callables,
    _collections,
    _dict_views,
    _flatten,
    _function,
    _functions,
    _generators,
    _iterables,
    _iterators,
    _lambda,
    _numbers,
    _obj,
    _objects,
    _primitives,
    _sequences,
    _singletons,
    _strings,
    _types,
    all_types,
    all_types_besides,
)
from katalytic.data import (
    as_dict_of_lists,
    as_list_of_dicts,
    as_list_of_lists,
    detect_fronts,
    detect_fronts_negative,
    detect_fronts_positive,
    detect_runs,
    first,
    first_with_idx,
    flatten,
    flatten_recursive,
    last,
    last_with_idx,
    map_dict_keys,
    map_dict_values,
    map_recursive,
    one,
    pick_all,
    pick_all_besides,
    pick_any,
    pop_max,
    pop_max_by_dict_key,
    pop_max_by_dict_value,
    pop_min,
    pop_min_by_dict_key,
    pop_min_by_dict_value,
    sort_dict_by_keys,
    sort_dict_by_keys_recursive,
    sort_dict_by_values,
    sort_dict_by_values_recursive,
    sort_recursive,
    swap_keys_and_values,
    xor,
    xor_with_idx,
)
from katalytic.data.checks import (
    dicts_share_key_order,
    dicts_share_value_order,
    is_equal,
    is_generator_function,
    is_iterator,
)


def _is_list(x):
    return isinstance(x, list)


def _is_negative(x):
    return _is_num(x) and x < 0


def _is_num(x):
    return isinstance(x, (int, float))


def _is_odd(x):
    return _is_num(x) and x % 2 == 1


def _is_str(x):
    return isinstance(x, str)


class Test_all_types:
    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, False, object()])
    def test_wrong_type(self, wrong_type):
        with pytest.raises(TypeError):
            all_types(wrong_type)

    @pytest.mark.parametrize("unexpected", [["iterable", "func", "strong"]])
    def test_unexpected(self, unexpected):
        with pytest.raises(ValueError):
            all_types(unexpected)

    @pytest.mark.parametrize(
        "whitelist, expected",
        [
            ("callables", _callables),
            ("collections", _collections),
            ("dict_views", _dict_views),
            ("functions", _functions),
            ("generators", _generators),
            ("iterators", _iterators),
            ("numbers", _numbers),
            ("objects", _objects),
            ("primitives", _primitives),
            ("sequences", _sequences),
            ("singletons", _singletons),
            ("strings", _strings),
            (None, _flatten(_types.values())),
            (["iterables", "objects", "path"], [*_iterables, *_objects, Path("")]),
            (["iterables"], _iterables),
        ],
    )
    def test_all_types(self, whitelist, expected):
        assert all_types(whitelist) == expected


class Test_all_types_besides:
    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, False, None, object()])
    def test_wrong_type(self, wrong_type):
        with pytest.raises(TypeError):
            all_types_besides(wrong_type)

    @pytest.mark.parametrize("unexpected", [["iterable", "func", "strong"]])
    def test_unexpected(self, unexpected):
        with pytest.raises(ValueError):
            all_types_besides(unexpected)

    @pytest.mark.parametrize(
        "blacklist, expected",
        [
            (
                ["iterables"],
                [
                    True,
                    False,
                    bytearray(b""),
                    b"",
                    _function,
                    _lambda,
                    _C_obj,
                    _C,
                    0j,
                    Decimal("0"),
                    0.0,
                    Fraction(0, 1),
                    0,
                    None,
                    _obj,
                    PosixPath("."),
                    "",
                ],
            ),
            (
                "iterables",
                [
                    True,
                    False,
                    bytearray(b""),
                    b"",
                    _function,
                    _lambda,
                    _C_obj,
                    _C,
                    0j,
                    Decimal("0"),
                    0.0,
                    Fraction(0, 1),
                    0,
                    None,
                    _obj,
                    PosixPath("."),
                    "",
                ],
            ),
            (
                ["iterables", "generators", "functions", "objects", "path"],
                [True, False, bytearray(b""), b"", _C, 0j, Decimal("0"), 0.0, Fraction(0, 1), 0, None, ""],
            ),
        ],
    )
    def test_all_types_besides(self, blacklist, expected):
        assert all_types_besides(blacklist) == expected


class Test_as_dict_of_lists:
    @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
    def test_precondition_empty_ok(self, mistake):
        with pytest.raises(TypeError):
            as_dict_of_lists([], empty_ok=mistake)

    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, False, None, object(), iter([]), map(lambda x: x, [])])
    def test_wrong_type(self, wrong_type):
        with pytest.raises(TypeError):
            as_dict_of_lists(wrong_type)

    @pytest.mark.parametrize(
        "data, expected",
        [
            # from dict of sequences
            [{"b": [3, 4], "a": [1, 2]}, {"b": [3, 4], "a": [1, 2]}],
            [{"a": (1, 2), "b": (3, 4)}, {"a": [1, 2], "b": [3, 4]}],
            # from sequence of dicts
            [({"a": 1, "b": 2}, {"b": 4, "a": 3}), {"a": [1, 3], "b": [2, 4]}],
            [[{"b": 2, "a": 1}, {"b": 4, "a": 3}], {"b": [2, 4], "a": [1, 3]}],
            # from sequence of sequences
            [[["b", "a"], [1, 2], [3, 4]], {"b": [1, 3], "a": [2, 4]}],
            [(("a", "b"), (1, 2), (3, 4)), {"a": [1, 3], "b": [2, 4]}],
        ],
    )
    def test_preserves_key_order_and_converts_seq_to_list(self, data, expected):
        actual = as_dict_of_lists(data)
        assert actual == expected
        assert list(actual.keys()) == list(expected.keys())

    @pytest.mark.parametrize("data", [[], (), {}])
    def test_empty_ok(self, data):
        assert as_dict_of_lists(data, empty_ok=True) == []

    @pytest.mark.parametrize("data", [[], (), {}])
    def test_empty_ok_False(self, data):
        with pytest.raises(ValueError):
            as_dict_of_lists(data, empty_ok=False)


class Test_as_list_of_dicts:
    @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
    def test_precondition_empty_ok(self, mistake):
        with pytest.raises(TypeError):
            as_list_of_dicts([], empty_ok=mistake)

    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, False, None, object(), iter([]), map(lambda x: x, [])])
    def test_wrong_type(self, wrong_type):
        with pytest.raises(TypeError):
            as_list_of_dicts(wrong_type)

    def test_different_keys(self):
        data = [{"a": 1, "b": 2}, {"c": 3, "d": 4, "e": 5}]
        with pytest.raises(TypeError):
            as_list_of_dicts(data)

    @pytest.mark.parametrize(
        "data, expected",
        [
            # from dict of sequences
            [{"a": [1, 2], "b": [3, 4]}, [{"a": 1, "b": 3}, {"a": 2, "b": 4}]],
            [{"b": (3, 4), "a": (1, 2)}, [{"b": 3, "a": 1}, {"b": 4, "a": 2}]],
            # from sequence of dicts
            [[{"b": 2, "a": 1}, {"a": 3, "b": 4}], [{"b": 2, "a": 1}, {"b": 4, "a": 3}]],
            [({"a": 1, "b": 2}, {"a": 3, "b": 4}), [{"a": 1, "b": 2}, {"a": 3, "b": 4}]],
            # from sequence of sequences
            [[["b", "a"], [1, 2], [3, 4]], [{"b": 1, "a": 2}, {"b": 3, "a": 4}]],
            [(["a", "b"], [1, 2], [3, 4]), [{"a": 1, "b": 2}, {"a": 3, "b": 4}]],
        ],
    )
    def test_preserves_key_order_and_converts_seq_to_list(self, data, expected):
        actual = as_list_of_dicts(data)
        keys = list(expected[0].keys())
        assert actual == expected
        assert all(list(d.keys()) == keys for d in actual)

    @pytest.mark.parametrize("data", [[], (), {}])
    def test_empty_ok(self, data):
        assert as_list_of_dicts(data, empty_ok=True) == []

    @pytest.mark.parametrize("data", [[], (), {}])
    def test_empty_ok_False(self, data):
        with pytest.raises(ValueError):
            as_list_of_dicts(data, empty_ok=False)


class Test_as_list_of_lists:
    @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
    def test_precondition_empty_ok(self, mistake):
        with pytest.raises(TypeError):
            as_list_of_lists([], empty_ok=mistake)

    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, False, None, object(), iter([]), map(lambda x: x, [])])
    def test_wrong_type(self, wrong_type):
        with pytest.raises(TypeError):
            as_list_of_lists(wrong_type)

    @pytest.mark.parametrize(
        "data, expected",
        [
            # from dict of sequences
            [{"a": [1, 2], "b": [3, 4]}, [["a", "b"], [1, 3], [2, 4]]],
            [{"b": (3, 4), "a": (1, 2)}, [["b", "a"], [3, 1], [4, 2]]],
            # from sequence of dicts
            [({"a": 1, "b": 2}, {"a": 3, "b": 4}), [["a", "b"], [1, 2], [3, 4]]],
            [[{"b": 2, "a": 1}, {"a": 3, "b": 4}], [["b", "a"], [2, 1], [4, 3]]],
            # from sequence of sequences
            [[["b", "a"], [1, 2], [3, 4]], [["b", "a"], [1, 2], [3, 4]]],
            [(["a", "b"], (1, 2), [3, 4]), [["a", "b"], [1, 2], [3, 4]]],
        ],
    )
    def test_preserves_key_order_and_converts_seq_to_list(self, data, expected):
        assert as_list_of_lists(data) == expected

    @pytest.mark.parametrize("data", [[], (), {}])
    def test_empty_ok(self, data):
        assert as_list_of_lists(data, empty_ok=True) == []

    @pytest.mark.parametrize("data", [[], (), {}])
    def test_empty_ok_False(self, data):
        with pytest.raises(ValueError):
            as_list_of_lists(data, empty_ok=False)


class Test_first:
    @pytest.mark.parametrize(
        "wrong_type", [iter([]), map(lambda x: x, []), range(1), object(), [], {}, (), set(), 1, True, False, None, ""]
    )
    def test_key_not_callable(self, wrong_type):
        with pytest.raises(TypeError):
            first([], condition=wrong_type)

    def test_sets_are_not_allowed(self):
        with pytest.raises(TypeError):
            first(set())

    @pytest.mark.parametrize("data", [iter([]), map(lambda x: x, []), [], {}, ()])
    def test_empty(self, data):
        assert first(data) is _UNDEFINED

    def test_no_first_with_condition(self):
        assert first(range(10), condition=lambda x: x > 50) is _UNDEFINED

    @pytest.mark.parametrize(
        "data, expected",
        [
            (range(10), 0),
            ([False, None, 5, True], False),
            (["", 0, None, False], ""),
            (map(lambda x: x + 1, range(0, 100, 10)), 1),
        ],
    )
    def test_first(self, data, expected):
        assert first(data) == expected


class Test_first_with_idx:
    @pytest.mark.parametrize(
        "wrong_type", [iter([]), map(lambda x: x, []), range(1), object(), [], {}, (), set(), 1, True, False, None, ""]
    )
    def test_key_not_callable(self, wrong_type):
        with pytest.raises(TypeError):
            first_with_idx([], condition=wrong_type)

    def test_sets_are_not_allowed(self):
        with pytest.raises(TypeError):
            first_with_idx(set())

    @pytest.mark.parametrize("data", [iter([]), map(lambda x: x, []), [], {}, ()])
    def test_empty(self, data):
        assert first_with_idx(data) is _UNDEFINED

    def test_no_first_with_condition(self):
        assert first_with_idx(range(10), condition=lambda x: x > 50) is _UNDEFINED

    def test_first_with_key(self):
        assert first_with_idx(range(5, 15), condition=lambda x: x >= 10) == (5, 10)

    @pytest.mark.parametrize(
        "data, expected",
        [
            (range(10), (0, 0)),
            ([False, None, 5, True], (0, False)),
            (["", 0, None, False], (0, "")),
            (map(lambda x: x + 1, range(0, 100, 10)), (0, 1)),
        ],
    )
    def test_first(self, data, expected):
        assert first_with_idx(data) == expected


class Test_last:
    @pytest.mark.parametrize(
        "wrong_type", [iter([]), map(lambda x: x, []), range(1), object(), [], {}, (), set(), 1, True, False, None, ""]
    )
    def test_key_not_callable(self, wrong_type):
        with pytest.raises(TypeError):
            last([], condition=wrong_type)

    def test_sets_are_not_allowed(self):
        with pytest.raises(TypeError):
            last(set())

    @pytest.mark.parametrize("data", [iter([]), map(lambda x: x, []), [], {}, ()])
    def test_empty(self, data):
        assert last(data) is _UNDEFINED

    def test_no_last_with_condition(self):
        assert last(range(10), condition=lambda x: x > 50) is _UNDEFINED

    @pytest.mark.parametrize(
        "data, expected",
        [
            (range(10), 9),
            ([False, None, 5, True], True),
            ([False, None, True, 5], 5),
            (["", 0, None, False], False),
            (map(lambda x: x + 1, range(0, 100, 10)), 91),
        ],
    )
    def test_last(self, data, expected):
        assert last(data) == expected


class Test_last_with_idx:
    @pytest.mark.parametrize(
        "wrong_type", [iter([]), map(lambda x: x, []), range(1), object(), [], {}, (), set(), 1, True, False, None, ""]
    )
    def test_key_not_callable(self, wrong_type):
        with pytest.raises(TypeError):
            last_with_idx([], condition=wrong_type)

    def test_sets_are_not_allowed(self):
        with pytest.raises(TypeError):
            last_with_idx(set())

    @pytest.mark.parametrize("data", [iter([]), map(lambda x: x, []), [], {}, ()])
    def test_empty(self, data):
        assert last_with_idx(data) is _UNDEFINED

    def test_no_last_with_condition(self):
        assert last_with_idx(range(10), condition=lambda x: x > 50) is _UNDEFINED

    def test_last_with_key(self):
        assert last_with_idx(range(5, 15), condition=lambda x: x <= 13) == (8, 13)

    @pytest.mark.parametrize(
        "data, expected",
        [
            (range(7, 10), (2, 9)),
            ([False, None, 5, True], (3, True)),
            (["", 0, None, False], (3, False)),
            (map(lambda x: x + 1, range(0, 100, 10)), (9, 91)),
        ],
    )
    def test_last(self, data, expected):
        assert last_with_idx(data) == expected


class Test_flatten:
    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, False, None, "", object()])
    def test_should_be_an_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            flatten(wrong_type)

    @pytest.mark.parametrize("empty", [[], (), {}, set(), iter([])])
    def test_empty(self, empty):
        assert flatten(empty) == []

    @pytest.mark.parametrize("data, expected", [([1, 2, 3], [1, 2, 3]), ((1, 2, 3), [1, 2, 3]), ({1, 2, 3}, [1, 2, 3])])
    def test_already_flat(self, data, expected):
        assert flatten(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ((1, [(2, 3), (4, (5, 6))]), [1, (2, 3), (4, (5, 6))]),
            ([[1, (2, 3), (4, (5, 6))]], [1, (2, 3), (4, (5, 6))]),
            ({1, (2, 3), (4, (5, 6))}, [1, 2, 3, 4, (5, 6)]),
        ],
    )
    def test_flattens_only_one_level(self, data, expected):
        actual = flatten(data)
        if isinstance(data, set):
            actual = set(actual)
            expected = set(expected)

        assert actual == expected


class Test_flatten_recursive:
    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, False, None, "", object()])
    def test_should_be_an_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            flatten_recursive(wrong_type)

    @pytest.mark.parametrize("empty", [[], (), {}, set(), iter([])])
    def test_empty(self, empty):
        assert flatten_recursive(empty) == []

    @pytest.mark.parametrize("data, expected", [([1, 2, 3], [1, 2, 3]), ((1, 2, 3), [1, 2, 3]), ({1, 2, 3}, [1, 2, 3])])
    def test_already_flat(self, data, expected):
        assert flatten_recursive(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ((1, [(2, 3), (4, (5, 6))]), [1, 2, 3, 4, 5, 6]),
            ([[1, (2, 3), (4, (5, 6))]], [1, 2, 3, 4, 5, 6]),
            ({1, (2, 3), (4, (5, 6))}, [1, 2, 3, 4, 5, 6]),
        ],
    )
    def test_flattens_all_levels(self, data, expected):
        actual = flatten_recursive(data)
        if isinstance(data, set):
            actual = set(actual)
            expected = set(expected)

        assert actual == expected


class Test_map_dict_keys:
    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, None, False, "string", object()])
    def test_mapping_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            map_dict_keys(wrong_type, {})

    @pytest.mark.parametrize("wrong_type", [[], set(), (), 1, 1.0, True, None, False, "string", object()])
    def test_not_a_dict(self, wrong_type):
        with pytest.raises(TypeError):
            map_dict_keys(lambda x: x, wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, False, "string", object()])
    def test_condition_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            map_dict_keys(lambda x: x, {}, condition=wrong_type)

    def test_empty(self):
        assert map_dict_keys(lambda x: x, {}) == {}

    def test_simple_mapping(self):
        assert map_dict_keys(str.upper, {"a": 1, "b": 2}) == {"A": 1, "B": 2}

    def test_conditioned_mapping(self):
        data = {"a": 1, (0, 1): 2}
        expected = {"A": 1, (0, 1): 2}
        assert map_dict_keys(str.upper, data, condition=_is_str) == expected


class Test_map_dict_values:
    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, None, False, "string", object()])
    def test_mapping_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            map_dict_values(wrong_type, {})

    @pytest.mark.parametrize("wrong_type", [[], set(), (), 1, 1.0, True, None, False, "string", object()])
    def test_not_a_dict(self, wrong_type):
        with pytest.raises(TypeError):
            map_dict_values(lambda x: x, wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, False, "string", object()])
    def test_condition_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            map_dict_values(lambda x: x, {}, condition=wrong_type)

    def test_empty(self):
        assert map_dict_values(lambda x: x, {}) == {}

    def test_simple_mapping(self):
        assert map_dict_values(str, {"a": 1, "b": 2}) == {"a": "1", "b": "2"}

    def test_conditioned_mapping(self):
        data = {"a": -1, (0, 1): 1}
        expected = {"a": "-1", (0, 1): 1}
        assert map_dict_values(str, data, condition=_is_negative) == expected


class Test_map_recursive:
    @pytest.mark.xfail(reason="Not implemented")
    def test_condition_is_iterable(self):
        """
        1. Should run both the `if is_iterable()` and the `if condition(x)` branches.
        2. Add another param for which of the two branches to run first"""
        assert 0

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, None, False, "string", object()])
    def test_mapping_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            map_recursive(wrong_type, {})

    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, None, False, "string", object()])
    def test_not_an_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            map_recursive(lambda x: x, wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, False, "string", object()])
    def test_condition_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            map_recursive(lambda x: x, {}, condition=wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_on_dict_keys_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            map_recursive(lambda x: x, {}, on_dict_keys=wrong_type)

    @pytest.mark.parametrize("data", [[], (), {}, set()])
    def test_empty(self, data):
        assert map_recursive(lambda x: x, data) == data

    def test_simple(self):
        assert map_recursive(lambda x: x + 1, [1, 2]) == [2, 3]
        assert map_recursive(lambda x: x + 1, (1, 2)) == (2, 3)
        assert map_recursive(lambda x: x + 1, {1, 2}) == {2, 3}
        assert map_recursive(lambda x: x + 1, {"a": 1, "b": 2}) == {"a": 2, "b": 3}

        actual = map_recursive(lambda x: x + 1, iter([1, 2]))
        assert is_iterator(actual)
        assert tuple(actual) == (2, 3)

    def test_deep(self):
        data = [(1, {"a": 1, "b": {1, 2}})]
        expected = [(2, {"a": 2, "b": {2, 3}})]
        assert map_recursive(lambda x: x + 1, data) == expected

    def test_deep_with_condition(self):
        data = [(1, 2, {"a": 1, "b": 2, "c": {1, (1, 2)}})]
        expected = [(2, 2, {"a": 2, "b": 2, "c": {2, (2, 2)}})]
        assert map_recursive(lambda x: x + 1, data, condition=_is_odd) == expected

    def test_deep_with_condition_2(self):
        data = [1, 2, (1, 2, {"a": 1, "b": [1, 2]})]
        expected = (1, 2, (1, 2, {"a": 1, "b": (1, 2)}))
        assert map_recursive(tuple, data, condition=_is_list) == expected

    def test_on_dict_keys(self):
        data = {"a": 1, "b": {"a": 1, "b": 2}}
        expected = {"A": 1, "B": {"A": 1, "B": 2}}
        assert map_recursive(lambda x: x.upper(), data, condition=_is_str, on_dict_keys=True) == expected

    def test_on_dict_keys_iter(self):
        data = {"a": 1, (1, 2): {"a": 1, (3, 4): 2}}
        expected = {"a": 2, (2, 3): {"a": 2, (4, 5): 3}}
        assert map_recursive(lambda x: x + 1, data, condition=_is_num, on_dict_keys=True) == expected


class Test_one:
    @pytest.mark.parametrize(
        "wrong_type", [iter([]), map(lambda x: x, []), range(1), object(), [], {}, (), set(), 1, True, False, None, ""]
    )
    def test_key_not_callable(self, wrong_type):
        with pytest.raises(TypeError):
            one([], condition=wrong_type)

    @pytest.mark.parametrize("wrong_type", [object(), 1, True, False, None, ""])
    def test_key_not_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            one(wrong_type)

    @pytest.mark.parametrize("data", [iter([]), map(lambda x: x, []), [], {}, (), set()])
    def test_empty(self, data):
        assert one(data) is _UNDEFINED

    @pytest.mark.parametrize("data", [{"", 0, None}, ["", 0, None, False]])
    def test_no_one(self, data):
        assert one(data) in data

    def test_no_one_with_condition(self):
        assert one(range(10), condition=lambda x: x > 50) is _UNDEFINED

    @pytest.mark.parametrize(
        "data, expected",
        [
            (range(10), 0),
            ([False, None, 5, True], False),
            ([False, None, True, 5], False),
            (map(lambda x: x + 1, range(0, 100, 10)), 1),
        ],
    )
    def test_one(self, data, expected):
        assert one(data) == expected

    @pytest.mark.parametrize("data", [{0, 1, 2, 3}, {3, 2, 1, 0}])
    def test_one_of_set(self, data):
        assert one(data) in data


class Test_pop_min:
    @pytest.mark.parametrize("wrong_type", all_types_besides("iterables"))
    def test_not_an_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            pop_min(wrong_type)

    def test_dict(self):
        with pytest.raises(TypeError):
            pop_min({})

    @pytest.mark.parametrize("wrong_type", all_types_besides("callables"))
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            pop_min([1], condition=wrong_type)

    @pytest.mark.parametrize("data", all_types("iterables"))
    def test_empty(self, data):
        if isinstance(data, dict):
            return
        elif is_generator_function(data):
            data = data()
            next(data)

        with pytest.raises(ValueError):
            pop_min(data)

    @pytest.mark.parametrize(
        "data, expected",
        [
            ([3, 2, 1, 4], (1, [3, 2, 4])),
            ((0, -1, 3, 4), (-1, (0, 3, 4))),
            (map(float, (0, 3, -4, 5)), (-4, [0, 3, 5])),
        ],
    )
    def test_no_key(self, data, expected):
        assert pop_min(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ([3, 2, 1, 4], (4, [3, 2, 1])),
            ((0, -1, 3, 4), (4, (0, -1, 3))),
            (map(float, (0, 3, -4, 5)), (5, [0, 3, -4])),
        ],
    )
    def test_with_key(self, data, expected):
        assert pop_min(data, condition=lambda x: -x) == expected


class Test_pop_max:
    @pytest.mark.parametrize("wrong_type", all_types_besides("iterables"))
    def test_not_an_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            pop_max(wrong_type)

    def test_dict(self):
        with pytest.raises(TypeError):
            pop_max({})

    @pytest.mark.parametrize("wrong_type", all_types_besides("callables"))
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            pop_max([1], condition=wrong_type)

    @pytest.mark.parametrize("data", all_types("iterables"))
    def test_empty(self, data):
        if isinstance(data, dict):
            return
        elif is_generator_function(data):
            data = data()
            next(data)

        with pytest.raises(ValueError):
            pop_max(data)

    @pytest.mark.parametrize(
        "data, expected",
        [
            ([3, 2, 1, 4], (4, [3, 2, 1])),
            ((0, -1, 3, 4), (4, (0, -1, 3))),
            (map(float, (0, 3, -4, 5)), (5, [0, 3, -4])),
        ],
    )
    def test_no_key(self, data, expected):
        assert pop_max(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ([3, 2, 1, 4], (1, [3, 2, 4])),
            ({0, -1, 3, 4}, (-1, {0, 3, 4})),
            (map(float, (0, 3, -4, 5)), (-4, [0, 3, 5])),
        ],
    )
    def test_with_key(self, data, expected):
        assert pop_max(data, condition=lambda x: -x) == expected


class Test_pop_max_by_dict_key:
    @pytest.mark.parametrize("wrong_type", all_types_besides("dict"))
    def test_not_a_dict(self, wrong_type):
        with pytest.raises(TypeError):
            pop_max_by_dict_key(wrong_type)

    @pytest.mark.parametrize("wrong_type", all_types_besides("callables"))
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            pop_max_by_dict_key({"1": 1}, condition=wrong_type)

    def test_empty(self):
        with pytest.raises(ValueError):
            pop_max_by_dict_key({})

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({"a": 3, "b": 2, "c": 1, "d": 4}, (("d", 4), {"a": 3, "b": 2, "c": 1})),
            ({"a": 0, "b": -1, "c": 4, "d": 3}, (("d", 3), {"a": 0, "b": -1, "c": 4})),
        ],
    )
    def test_no_key(self, data, expected):
        assert pop_max_by_dict_key(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({3: "a", 2: "b", 1: "c", 4: "d"}, ((1, "c"), {3: "a", 2: "b", 4: "d"})),
            ({0: "a", -1: "b", 4: "c", 3: "d"}, ((-1, "b"), {0: "a", 4: "c", 3: "d"})),
        ],
    )
    def test_with_key(self, data, expected):
        assert pop_max_by_dict_key(data, condition=lambda x: -x) == expected


class Test_pop_min_by_dict_key:
    @pytest.mark.parametrize("wrong_type", all_types_besides("dict"))
    def test_not_a_dict(self, wrong_type):
        with pytest.raises(TypeError):
            pop_min_by_dict_key(wrong_type)

    @pytest.mark.parametrize("wrong_type", all_types_besides("callables"))
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            pop_min_by_dict_key({"1": 1}, condition=wrong_type)

    def test_empty(self):
        with pytest.raises(ValueError):
            pop_min_by_dict_key({})

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({"a": 3, "b": 2, "c": 1, "d": 4}, (("a", 3), {"b": 2, "c": 1, "d": 4})),
            ({"a": 0, "b": -1, "c": 4, "d": 3}, (("a", 0), {"b": -1, "c": 4, "d": 3})),
        ],
    )
    def test_no_key(self, data, expected):
        assert pop_min_by_dict_key(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({3: "a", 2: "b", 1: "c", 4: "d"}, ((4, "d"), {3: "a", 2: "b", 1: "c"})),
            ({0: "a", -1: "b", 4: "c", 3: "d"}, ((4, "c"), {0: "a", -1: "b", 3: "d"})),
        ],
    )
    def test_with_key(self, data, expected):
        assert pop_min_by_dict_key(data, condition=lambda x: -x) == expected


class Test_pop_max_by_dict_value:
    @pytest.mark.parametrize("wrong_type", all_types_besides("dict"))
    def test_not_a_dict(self, wrong_type):
        with pytest.raises(TypeError):
            pop_max_by_dict_value(wrong_type)

    @pytest.mark.parametrize("wrong_type", all_types_besides("callables"))
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            pop_max_by_dict_value({"1": 1}, condition=wrong_type)

    def test_empty(self):
        with pytest.raises(ValueError):
            pop_max_by_dict_value({})

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({"a": 3, "b": 2, "c": 1, "d": 4}, (("d", 4), {"a": 3, "b": 2, "c": 1})),
            ({"a": 0, "b": -1, "c": 4, "d": 3}, (("c", 4), {"a": 0, "b": -1, "d": 3})),
        ],
    )
    def test_no_key(self, data, expected):
        assert pop_max_by_dict_value(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({3: "a", 2: "b", 1: "c", 4: "d"}, ((3, "a"), {2: "b", 1: "c", 4: "d"})),
            ({0: "a", -1: "b", 4: "c", 3: "d"}, ((0, "a"), {-1: "b", 4: "c", 3: "d"})),
        ],
    )
    def test_with_key(self, data, expected):
        assert pop_max_by_dict_value(data, condition=lambda x: -ord(x)) == expected


class Test_pop_min_by_dict_value:
    @pytest.mark.parametrize("wrong_type", all_types_besides("dict"))
    def test_not_a_dict(self, wrong_type):
        with pytest.raises(TypeError):
            pop_min_by_dict_value(wrong_type)

    @pytest.mark.parametrize("wrong_type", all_types_besides("callables"))
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            pop_min_by_dict_value({"1": 1}, condition=wrong_type)

    def test_empty(self):
        with pytest.raises(ValueError):
            pop_min_by_dict_value({})

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({"a": 3, "b": 2, "c": 1, "d": 4}, (("c", 1), {"a": 3, "b": 2, "d": 4})),
            ({"a": 0, "b": -1, "c": 4, "d": 3}, (("b", -1), {"a": 0, "c": 4, "d": 3})),
        ],
    )
    def test_no_key(self, data, expected):
        assert pop_min_by_dict_value(data) == expected

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({3: "a", 2: "b", 1: "c", 4: "d"}, ((4, "d"), {3: "a", 2: "b", 1: "c"})),
            ({0: "a", -1: "b", 4: "c", 3: "d"}, ((3, "d"), {0: "a", -1: "b", 4: "c"})),
        ],
    )
    def test_with_key(self, data, expected):
        assert pop_min_by_dict_value(data, condition=lambda x: -ord(x)) == expected


class Test_pick_all:
    @pytest.mark.parametrize("wrong_type", [object(), 1, True, False, None, ""])
    def test_needles_should_be_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            pick_all(wrong_type, [])

    @pytest.mark.parametrize("wrong_type", [object(), 1, True, False, None, ""])
    def test_haystack_should_be_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            pick_all([], wrong_type)

    @pytest.mark.parametrize("needles, haystack, expected", [([], [], []), ((), {}, []), ((), [1], []), ((1,), [], [])])
    def test_empty(self, needles, haystack, expected):
        assert pick_all(needles, haystack) == expected

    @pytest.mark.parametrize("needles, haystack, expected", [([1, 2], [3, 4], []), ([0, True], (1, False), [])])
    def test_no_match(self, needles, haystack, expected):
        assert pick_all(needles, haystack) == expected

    @pytest.mark.parametrize(
        "needles, haystack, expected",
        [([1, 2, 3], [2, 3, 4], [2, 3]), ([False, True, None], {True, None}, [True, None])],
    )
    def test_match(self, needles, haystack, expected):
        assert pick_all(needles, haystack) == expected


class Test_pick_all_besides:
    @pytest.mark.parametrize("wrong_type", [object(), 1, True, False, None, ""])
    def test_needles_should_be_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            pick_all_besides(wrong_type, [])

    @pytest.mark.parametrize("wrong_type", [object(), 1, True, False, None, ""])
    def test_haystack_should_be_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            pick_all_besides([], wrong_type)

    @pytest.mark.parametrize("needles, haystack, expected", [([], [], []), ((), {}, [])])
    def test_empty(self, needles, haystack, expected):
        assert pick_all_besides(needles, haystack) == expected

    @pytest.mark.parametrize(
        "needles, haystack, expected", [([1, 2, 3], [3, 4, 5], [1, 2]), ([0, True, None], {1, False, None}, [0, True])]
    )
    def test_match(self, needles, haystack, expected):
        assert pick_all_besides(needles, haystack) == expected

    @pytest.mark.parametrize(
        "needles, haystack, expected", [([1, 2, 3], [1, 2, 3], []), ([False, True, None], {False, True, None}, [])]
    )
    def test_no_match(self, needles, haystack, expected):
        assert pick_all_besides(needles, haystack) == expected


class Test_pick_any:
    @pytest.mark.parametrize("wrong_type", [object(), 1, True, False, None, ""])
    def test_needles_should_be_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            pick_any(wrong_type, [])

    @pytest.mark.parametrize("wrong_type", [object(), 1, True, False, None, ""])
    def test_haystack_should_be_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            pick_any([], wrong_type)

    @pytest.mark.parametrize(
        "needles, haystack, expected", [([], [], None), ((), {}, None), ((), [1], None), ((1,), [], None)]
    )
    def test_empty(self, needles, haystack, expected):
        assert pick_any(needles, haystack) == expected

    @pytest.mark.parametrize("needles, haystack, expected", [([1, 2], [3, 4], None), ([0, True], {1, False}, None)])
    def test_no_match(self, needles, haystack, expected):
        assert pick_any(needles, haystack) == expected

    @pytest.mark.parametrize(
        "needles, haystack, expected", [([1, 2, 3], [2, 3, 4], 2), ([False, True, None], {None, True}, True)]
    )
    def test_match(self, needles, haystack, expected):
        assert pick_any(needles, haystack) == expected


class Test_sort_dict_by_keys:
    @pytest.mark.parametrize("wrong_type", [[], set(), (), 1, 1.0, True, None, False, "string", object()])
    def test_not_a_dict(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_keys(wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, False, "string", object()])
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_keys({}, condition=wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_not_a_bool(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_keys({}, reverse=wrong_type)

    def test_empty(self):
        assert sort_dict_by_keys({}) == {}

    def test_simple(self):
        actual = sort_dict_by_keys({"b": 2, "c": 1, "a": 3})
        expected = {"a": 3, "b": 2, "c": 1}
        assert actual == expected
        assert dicts_share_key_order(actual, expected)

    def test_with_key(self):
        actual = sort_dict_by_keys({"qwerty": 1, "x": 3, "asd": 2}, condition=len)
        expected = {"x": 3, "asd": 2, "qwerty": 1}
        assert actual == expected
        assert dicts_share_key_order(actual, expected)

    def test_reversed(self):
        actual = sort_dict_by_keys({"b": 2, "c": 1, "a": 3}, reverse=True)
        expected = {"c": 1, "b": 2, "a": 3}
        assert actual == expected
        assert dicts_share_key_order(actual, expected)

    def test_with_key_and_reversed(self):
        actual = sort_dict_by_keys({"qwerty": 1, "x": 3, "asd": 2}, condition=len, reverse=True)
        expected = {"qwerty": 1, "asd": 2, "x": 3}
        assert actual == expected
        assert dicts_share_key_order(actual, expected)


class Test_sort_dict_by_values:
    @pytest.mark.parametrize("wrong_type", [[], set(), (), 1, 1.0, True, None, False, "string", object()])
    def test_not_a_dict(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_values(wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, False, "string", object()])
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_values({}, condition=wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_not_a_bool(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_values({}, reverse=wrong_type)

    def test_empty(self):
        assert sort_dict_by_values({}) == {}

    def test_simple(self):
        actual = sort_dict_by_values({"b": 2, "c": 1, "a": 3})
        expected = {"c": 1, "b": 2, "a": 3}
        assert actual == expected
        assert dicts_share_value_order(actual, expected)

    def test_with_key(self):
        actual = sort_dict_by_values({"qwerty": 1, "x": 3, "asd": -2}, condition=abs)
        expected = {"qwerty": 1, "asd": -2, "x": 3}
        assert actual == expected
        assert dicts_share_value_order(actual, expected)

    def test_reversed(self):
        actual = sort_dict_by_values({"b": 2, "c": 1, "a": 3}, reverse=True)
        expected = {"a": 3, "b": 2, "c": 1}
        assert actual == expected
        assert dicts_share_value_order(actual, expected)

    def test_with_key_and_reversed(self):
        actual = sort_dict_by_values({"qwerty": 1, "x": 3, "asd": -2}, condition=abs, reverse=True)
        expected = {"x": 3, "asd": -2, "qwerty": 1}
        assert actual == expected
        assert dicts_share_value_order(actual, expected)


class Test_sort_dict_by_keys_recursive:
    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, None, False, "string", object()])
    def test_not_an_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_keys_recursive(wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, False, "string", object()])
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_keys_recursive({}, condition=wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_not_a_bool(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_keys_recursive({}, reverse=wrong_type)

    def test_empty(self):
        assert sort_dict_by_keys_recursive({}) == {}

    @pytest.mark.parametrize(
        "data, expected", [[{"x": 1, "a": 2}, {"a": 2, "x": 1}], [{"a": 2, "x": 1}, {"a": 2, "x": 1}]]
    )
    def test_simple(self, data, expected):
        actual = sort_dict_by_keys_recursive(data)
        assert actual == expected
        assert dicts_share_key_order(actual, expected, recursive=True)

    @pytest.mark.parametrize(
        "data, expected",
        [
            [
                [{"x": 1, "a": 2}, map(lambda x: x, (2, 1, {"x": 1, "a": {"z": 1, "y": 2}}))],
                [{"a": 2, "x": 1}, (2, 1, {"a": {"y": 2, "z": 1}, "x": 1})],
            ],
            [
                [{"a": 2, "x": 1}, map(lambda x: x, (2, 1, {"a": {"y": 2, "z": 1}, "x": 1}))],
                [{"a": 2, "x": 1}, (2, 1, {"a": {"y": 2, "z": 1}, "x": 1})],
            ],
        ],
    )
    def test_recursive(self, data, expected):
        actual = sort_dict_by_keys_recursive(data)
        actual[1] = tuple(actual[1])
        assert actual == expected
        assert dicts_share_key_order(actual, expected, recursive=True)

    @pytest.mark.parametrize(
        "data, expected",
        [
            [
                [{"x": 1, "a": 2}, map(lambda x: x, (2, 1, {"x": 1, "a": {"z": 1, "y": 2}}))],
                [{"x": 1, "a": 2}, (2, 1, {"x": 1, "a": {"y": 2, "z": 1}})],
            ],
            [
                [{"a": 2, "x": 1}, map(lambda x: x, (2, 1, {"a": {"y": 2, "z": 1}, "x": 1}))],
                [{"x": 1, "a": 2}, (2, 1, {"x": 1, "a": {"y": 2, "z": 1}})],
            ],
        ],
    )
    def test_recursive_with_key(self, data, expected):
        def condition(k):
            if k in ["x", "y"]:
                return 0
            else:
                return ord(k)

        actual = sort_dict_by_keys_recursive(data, condition=condition)
        actual[1] = tuple(actual[1])
        assert actual == expected
        assert dicts_share_key_order(actual, expected, recursive=True)

    @pytest.mark.parametrize(
        "data, expected",
        [
            [
                [{"x": 1, "a": 2}, map(lambda x: x, (2, 1, {"x": 1, "a": {"z": 1, "y": 2}}))],
                [{"x": 1, "a": 2}, (2, 1, {"x": 1, "a": {"z": 1, "y": 2}})],
            ],
            [
                [{"a": 2, "x": 1}, map(lambda x: x, (2, 1, {"a": {"y": 2, "z": 1}, "x": 1}))],
                [{"x": 1, "a": 2}, (2, 1, {"x": 1, "a": {"z": 1, "y": 2}})],
            ],
        ],
    )
    def test_recursive_reversed(self, data, expected):
        actual = sort_dict_by_keys_recursive(data, reverse=True)
        actual[1] = tuple(actual[1])
        assert actual == expected
        assert dicts_share_key_order(actual, expected, recursive=True)


class Test_sort_dict_by_values_recursive:
    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, None, False, "string", object()])
    def test_not_an_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_values_recursive(wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, True, False, "string", object()])
    def test_key_is_not_a_function(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_values_recursive({}, condition=wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_not_a_bool(self, wrong_type):
        with pytest.raises(TypeError):
            sort_dict_by_values_recursive({}, reverse=wrong_type)

    def test_empty(self):
        assert sort_dict_by_values_recursive({}) == {}

    def test_simple(self):
        actual = sort_dict_by_values_recursive({"x": 2, "a": 1})
        expected = {"a": 1, "x": 2}
        assert actual == expected
        assert dicts_share_value_order(actual, expected, recursive=True)

    @pytest.mark.parametrize(
        "data, expected",
        [
            [
                [{"a": 2, "b": 1}, map(lambda x: x, (2, 1, {"a": 2, "b": 1}))],
                [{"b": 1, "a": 2}, (2, 1, {"b": 1, "a": 2})],
            ],
            [
                [{"b": 1, "a": 2}, map(lambda x: x, (2, 1, {"b": 1, "a": 2}))],
                [{"b": 1, "a": 2}, (2, 1, {"b": 1, "a": 2})],
            ],
        ],
    )
    def test_recursive(self, data, expected):
        actual = sort_dict_by_values_recursive(data)
        actual[1] = tuple(actual[1])
        assert actual == expected
        assert dicts_share_value_order(actual, expected, recursive=True)


class Test_sort_recursive:
    @pytest.mark.parametrize("wrong_type", [1, 1.0, True, None, False, "string", object()])
    def test_data_should_be_an_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            sort_recursive(wrong_type)

    @pytest.mark.parametrize(
        "wrong_type", [iter([]), map(lambda x: x, []), range(1), object(), [], {}, (), set(), 1, True, False, None, ""]
    )
    def test_key_should_be_callable(self, wrong_type):
        with pytest.raises(TypeError):
            sort_recursive([], condition=wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_reverse_should_be_a_bool(self, wrong_type):
        with pytest.raises(TypeError):
            sort_recursive({}, reverse=wrong_type)

    @pytest.mark.parametrize("wrong_value", [[], set(), (), {}, 1, 1.0, "string", object(), True, False])
    def test_sort_dicts_by_be_keys_values_or_None(self, wrong_value):
        with pytest.raises(ValueError):
            sort_recursive({}, sort_dicts_by=wrong_value)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_sort_iters_should_be_bool(self, wrong_type):
        with pytest.raises(TypeError):
            sort_recursive({}, sort_iters=wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_sort_lists_should_be_bool(self, wrong_type):
        with pytest.raises(TypeError):
            sort_recursive({}, sort_lists=wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_sort_sets_should_be_bool(self, wrong_type):
        with pytest.raises(TypeError):
            sort_recursive({}, sort_sets=wrong_type)

    @pytest.mark.parametrize("wrong_type", [[], set(), (), {}, 1, 1.0, None, "string", object()])
    def test_sort_tuples_should_be_bool(self, wrong_type):
        with pytest.raises(TypeError):
            sort_recursive({}, sort_tuples=wrong_type)

    @pytest.mark.parametrize(
        "data, expected", [([], []), ((), ()), ({}, {}), (set(), []), (iter([]), []), (map(bool, []), [])]
    )
    def test_sort_empty(self, data, expected):
        assert sort_recursive(data) == expected

    @pytest.mark.parametrize("data", [[], (), {}, set(), iter([]), map(bool, [])])
    def test_returns_same_type_if_possible(self, data):
        if isinstance(data, (list, tuple, dict)):
            assert isinstance(sort_recursive(data), type(data))
        elif isinstance(data, set) or is_iterator(data):
            assert isinstance(sort_recursive(data), list)

    @pytest.mark.parametrize(
        "data, expected",
        [
            ([3, 2, 1], [1, 2, 3]),
            ((3, 2, 1), (1, 2, 3)),
            ({3: "x", 2: "x", 1: "x"}, {1: "x", 2: "x", 3: "x"}),
            ({3, 2, 1}, [1, 2, 3]),
            (iter([3, 2, 1]), [1, 2, 3]),
            (map(bool, [2, 0, 1]), [False, True, True]),
        ],
    )
    def test_sort_simple(self, data, expected):
        assert sort_recursive(data) == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            ({"data": [3, 2, 1], "sort_lists": False}, [3, 2, 1]),
            ({"data": (3, 2, 1), "sort_tuples": False}, (3, 2, 1)),
            ({"data": {3: "x", 2: "x", 1: "x"}, "sort_dicts_by": None}, {3: "x", 2: "x", 1: "x"}),
            ({"data": {3, 2, 1}, "sort_sets": False}, {3, 2, 1}),
            ({"data": iter([3, 2, 1]), "sort_iters": False}, iter([3, 2, 1])),
            ({"data": map(bool, [2, 0, 1]), "sort_iters": False}, map(bool, [2, 0, 1])),
        ],
    )
    def test_type_remains_unchanged_when_not_sorting(self, kwargs, expected):
        actual = sort_recursive(**kwargs)

        if is_iterator(kwargs["data"]):
            assert is_iterator(actual)
            assert list(actual) == list(expected)
        else:
            assert isinstance(actual, type(kwargs["data"]))
            assert actual == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            ({"data": [(3, 5), (4, 2), (6, 1)], "sort_lists": False}, [(3, 5), (2, 4), (1, 6)]),
            ({"data": ([3, 5], [4, 2], [6, 1]), "sort_tuples": False}, ([3, 5], [2, 4], [1, 6])),
        ],
    )
    def test_sort_only_inner(self, kwargs, expected):
        actual = sort_recursive(**kwargs)
        if is_iterator(expected):
            assert list(actual) == list(expected)
        else:
            assert actual == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            ({"data": [(3, 5), (4, 2), (6, 1)]}, [(1, 6), (2, 4), (3, 5)]),
            ({"data": ([3, 5], [4, 2], [6, 1])}, ([1, 6], [2, 4], [3, 5])),
            ({"data": {"a": (2, 3), "b": (4, 1)}, "sort_dicts_by": "values"}, {"b": (1, 4), "a": (2, 3)}),
        ],
    )
    def test_sort_recursive(self, kwargs, expected):
        if is_iterator(expected):
            assert list(sort_recursive(**kwargs)) == list(expected)
        else:
            assert sort_recursive(**kwargs) == expected


class Test_swap_keys_and_values:
    @pytest.mark.parametrize("wrong_type", all_types_besides("dict"))
    def test_wrong_type(self, wrong_type):
        with pytest.raises(TypeError):
            swap_keys_and_values(wrong_type)

    @pytest.mark.parametrize(
        "data, expected", [({1: 2}, {2: 1}), ({1: "a", 3: "b"}, {"a": 1, "b": 3}), ({1: 2, 3: 2}, {2: 3}), ({}, {})]
    )
    def test_simple(self, data, expected):
        assert swap_keys_and_values(data) == expected


class Test_xor:
    @pytest.mark.parametrize(
        "wrong_type", [iter([]), map(lambda x: x, []), range(1), object(), [], {}, (), set(), 1, True, False, None, ""]
    )
    def test_key_should_be_callable(self, wrong_type):
        with pytest.raises(TypeError):
            xor(1, 2, condition=wrong_type)

    @pytest.mark.parametrize("values", [[], [1]])
    def test_at_least_2_values(self, values):
        with pytest.raises(ValueError):
            xor(*values)

    @pytest.mark.parametrize("values", [[0, None, False], [1, 2]])
    def test_none(self, values):
        assert xor(*values) is None

    @pytest.mark.parametrize("values, expected", [([0, None, 2, False], 2), ([1, 0], 1), ([0, True], True)])
    def test_ok(self, values, expected):
        assert is_equal(xor(*values), expected)


class Test_xor_with_idx:
    @pytest.mark.parametrize(
        "wrong_type", [iter([]), map(lambda x: x, []), range(1), object(), [], {}, (), set(), 1, True, False, None, ""]
    )
    def test_key_should_be_callable(self, wrong_type):
        with pytest.raises(TypeError):
            xor_with_idx(1, 2, condition=wrong_type)

    @pytest.mark.parametrize("values", [[], [1]])
    def test_at_least_2_values(self, values):
        with pytest.raises(ValueError):
            xor_with_idx(*values)

    @pytest.mark.parametrize("values", [[0, None, False], [1, 2]])
    def test_none(self, values):
        assert xor_with_idx(*values) is None

    @pytest.mark.parametrize(
        "values, expected", [([0, None, 5, False], (2, 5)), ([1, 0], (0, 1)), ([0, True], (1, True))]
    )
    def test_ok(self, values, expected):
        actual = xor_with_idx(*values)
        assert is_equal(actual, expected)


class Test_detect_fronts:
    @pytest.mark.parametrize(
        "wrong_type", [iter([]), map(lambda x: x, []), range(1), object(), [], {}, (), set(), None, ""]
    )
    def test_only_values_considered_bits_are_allowed(self, wrong_type):
        with pytest.raises(ValueError):
            detect_fronts([0, 1, wrong_type, True, False])

        with pytest.raises(ValueError):
            detect_fronts([1, 1, 0, 0, 0, 2])

    @pytest.mark.parametrize("values, expected", [([], []), ([0, 0, 0], [(0, 0)]), ([1, 1, 1], [(0, 1)])])
    def test_none(self, values, expected):
        assert detect_fronts(values) == expected

    def test_from_string(self):
        expected = [(0, 0), (3, 1), (4, 0), (6, 1), (7, 0), (8, 1), (11, 0), (12, 1), (14, 0)]
        assert detect_fronts("000100101110110") == expected

    def test_from_iter(self):
        expected = [(0, 0), (3, 1), (4, 0), (6, 1), (7, 0), (8, 1), (11, 0), (12, 1), (14, 0)]
        assert detect_fronts(map(int, "000100101110110")) == expected

    def test_detect_fronts_positive(self):
        assert detect_fronts_positive([0, 1, Decimal(0), Fraction(1)]) == [1, 3]
        assert detect_fronts_positive([1, 0]) == [0]

    def test_detect_fronts_negative(self):
        assert detect_fronts_negative([1, 0, 1, 0j]) == [1, 3]
        assert detect_fronts_negative([0, 1]) == [0]


class Test_detect_runs:
    @pytest.mark.parametrize(
        "values, expected",
        [
            ([], []),
            # ints and floats are grouped together if their value is equal
            ([0, 0.0, "0", False], [(0, 1, 2, 0), (2, 2, 1, "0"), (3, 3, 1, False)]),
            ([1, 1.0, "1", True], [(0, 1, 2, 1), (2, 2, 1, "1"), (3, 3, 1, True)]),
            (
                ["hello", "hello", "world", 42, 42.0, complex(42), Fraction(42)],
                [(0, 1, 2, "hello"), (2, 2, 1, "world"), (3, 6, 4, 42)],
            ),
        ],
    )
    def test_mixed_types(self, values, expected):
        assert detect_runs(values) == expected

        def test_from_string(self):
            expected = [
                (0, 2, 3, 0),
                (3, 3, 1, 1),
                (4, 5, 2, 0),
                (6, 6, 1, 1),
                (7, 7, 1, 0),
                (8, 10, 3, 1),
                (11, 11, 1, 0),
                (12, 13, 2, 1),
                (14, 14, 1, 0),
            ]
            assert detect_runs("000100101110110") == expected

    def test_from_iter(self):
        expected = [
            (0, 2, 3, 0),
            (3, 3, 1, 1),
            (4, 5, 2, 0),
            (6, 6, 1, 1),
            (7, 7, 1, 0),
            (8, 10, 3, 1),
            (11, 11, 1, 0),
            (12, 13, 2, 1),
            (14, 14, 1, 0),
        ]
        assert detect_runs(map(int, "000100101110110")) == expected
