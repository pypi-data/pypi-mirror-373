import pytest

from katalytic._pkg import all_types_besides
from katalytic.maths import L1, L2, clip, min_max


class Test_L1:
    @pytest.mark.parametrize("x", all_types_besides(["int", "float"]))
    def test_wrong_value(self, x):
        with pytest.raises(ValueError):
            L1(x, 1)

        with pytest.raises(ValueError):
            L1(1, x)

    @pytest.mark.parametrize("a, b", [([], []), ([], [1]), ([1, 2], [1]), ([[1]], [1])])
    def test_wrong_format(self, a, b):
        with pytest.raises(ValueError):
            L1(a, b)

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (1, 1, 0),
            (1, 5, 4),
            (-5, 1, 6),
            ([1], [3], 2),
            ([3], [1], 2),
            ([1, 2], [3, 4], 4),
            ([1.1, 2], [3, 3.5], 3.4),
            ([1, 10, 1], (10, 10, 10), 18),
        ],
    )
    def test_ok(self, a, b, expected):
        assert L1(a, b) == expected


class Test_L2:
    @pytest.mark.parametrize("x", all_types_besides(["int", "float"]))
    def test_wrong_value(self, x):
        with pytest.raises(ValueError):
            L2(x, 1)

        with pytest.raises(ValueError):
            L2(1, x)

    @pytest.mark.parametrize(
        "a, b",
        [
            ([], []),
            ([], [1]),
            ([1, 2], [1]),
            ([[1]], [1]),
            (["1"], [1]),
            ([True], [1]),
        ],
    )
    def test_wrong_value_2(self, a, b):
        with pytest.raises(ValueError):
            L2(a, b)

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (1, 1, 0),
            (1, 5, 4),
            (-5, 1, 6),
            ([1], [3], 2),
            ([3], [1], 2),
            ([1, 2], [5, 6], 5.656854),
            ([1, 10, 1], (10, 10, 10), 12.727922),
        ],
    )
    def test_ok(self, a, b, expected):
        assert round(L2(a, b), 6) == expected


class Test_min_max:
    @pytest.mark.parametrize("wrong_type", all_types_besides(["iterables"]))
    def test_not_an_iterable(self, wrong_type):
        with pytest.raises(TypeError):
            min_max(wrong_type)

    @pytest.mark.parametrize("wrong_type", all_types_besides(["callables", "none"]))
    def test_not_a_callable(self, wrong_type):
        with pytest.raises(TypeError):
            min_max([], key=wrong_type)

    @pytest.mark.parametrize(
        "data",
        [
            [],
            (),
            iter([]),
        ],
    )
    def test_empty_without_default(self, data):
        with pytest.raises(ValueError):
            min_max(data)

    @pytest.mark.parametrize(
        "data, default",
        [
            ([], "default_1"),
            ((), "default_2"),
            (iter([]), "default_3"),
        ],
    )
    def test_empty_with_default(self, data, default):
        assert min_max(data, default=default) == default

    @pytest.mark.parametrize(
        "data, expected",
        [
            ({3, 2, 1}, (1, 3)),
            ([3, 2, -1, 100], (-1, 100)),
        ],
    )
    def test_happy_path(self, data, expected):
        assert min_max(data) == expected


class Test_clip:
    @pytest.mark.parametrize("wrong_type", all_types_besides("numbers"))
    def test_wrong_type_x(self, wrong_type):
        with pytest.raises(TypeError):
            clip(wrong_type, 1, 2)

    @pytest.mark.parametrize("wrong_type", all_types_besides("numbers"))
    def test_wrong_type_min(self, wrong_type):
        with pytest.raises(TypeError):
            clip(1, wrong_type, 2)

    @pytest.mark.parametrize("wrong_type", all_types_besides("numbers"))
    def test_wrong_type_max(self, wrong_type):
        with pytest.raises(TypeError):
            clip(1, 2, wrong_type)

    @pytest.mark.parametrize(
        "args, expected",
        [
            ((2, 1, 3), 2),
            ((2.5, 2, 3), 2.5),
        ],
    )
    def test_within_bounds(self, args, expected):
        assert clip(*args) == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            ((20, 1, 3), 3),
            ((0.5, 2, 3), 2),
        ],
    )
    def test_outside_bounds(self, args, expected):
        assert clip(*args) == expected
