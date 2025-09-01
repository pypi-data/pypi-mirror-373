from pathlib import Path

import pytest as pytest

from katalytic._pkg import all_types_besides
from katalytic.meta import extract_call_stack_info, reference_caller_function


def _f0(depth):
    return reference_caller_function(depth=depth)


def _f1(depth):
    return _f0(depth)


def _f2(depth):
    return _f1(depth)


def _g0(depth):
    return extract_call_stack_info(depth=depth)


def _g1(depth):
    return _g0(depth)


def _g2(depth):
    return _g1(depth)


class _Nested_0:
    class Nested_1:
        def f0(depth):
            return extract_call_stack_info(depth=depth)

        def f1(depth):
            return _Nested_0.Nested_1.f0(depth)

        def f2(depth):
            return _Nested_0.Nested_1.f1(depth)


class Test_extract_call_stack_info:
    @pytest.mark.parametrize(
        "caller, depth, expected",
        [
            (_Nested_0.Nested_1.f1, 0, _Nested_0.Nested_1.f0),
            (_Nested_0.Nested_1.f1, 1, _Nested_0.Nested_1.f1),
            (_Nested_0.Nested_1.f2, 0, _Nested_0.Nested_1.f0),
            (_Nested_0.Nested_1.f2, 1, _Nested_0.Nested_1.f1),
            (_Nested_0.Nested_1.f2, 2, _Nested_0.Nested_1.f2),
        ],
    )
    def test_depth_ok_nested(self, caller, depth, expected):
        path, func, line = caller(depth=depth)

        assert path == str(Path(__file__).resolve())
        assert func == expected
        assert isinstance(line, int) and line > 0

    @pytest.mark.parametrize(
        "caller, depth, expected",
        [
            (_g1, 0, _g0),
            (_g1, 1, _g1),
            (_g2, 0, _g0),
            (_g2, 1, _g1),
            (_g2, 2, _g2),
        ],
    )
    def test_depth_ok(self, caller, depth, expected):
        path, func, line = caller(depth=depth)

        assert path == str(Path(__file__).resolve())
        assert func == expected
        assert isinstance(line, int) and line > 0

    def test_precondition_depth_should_be_positive(self):
        with pytest.raises(ValueError):
            _g1(-1)

    def test_depth_should_not_be_larger_than_the_stack(self):
        with pytest.raises(ValueError):
            # Use a large number because of the pytest internal calls
            _g1(100)

    @pytest.mark.parametrize("depth", all_types_besides("int"))
    def test_precondition_depth_should_be_an_integer(self, depth):
        with pytest.raises(TypeError):
            _g1(depth)


class Test_reference_caller_function:
    @pytest.mark.parametrize(
        "caller, depth, expected",
        [
            (_f1, 0, _f0),
            (_f1, 1, _f1),
            (_f2, 0, _f0),
            (_f2, 1, _f1),
            (_f2, 2, _f2),
        ],
    )
    def test_depth_ok(self, caller, depth, expected):
        assert caller(depth=depth) == expected

    def test_precondition_depth_should_be_positive(self):
        with pytest.raises(ValueError):
            _f1(-1)

    def test_depth_should_not_be_larger_than_the_stack(self):
        with pytest.raises(ValueError):
            # Use a large number because of the pytest internal calls
            _f1(100)

    @pytest.mark.parametrize("depth", all_types_besides("int"))
    def test_precondition_depth_should_be_an_integer(self, depth):
        with pytest.raises(TypeError):
            _f1(depth)
