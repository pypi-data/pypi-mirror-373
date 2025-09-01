import pytest

from katalytic import __version__
from katalytic._pkg import (
    _check,
    find_functions_marked_with,
    get_katalytic_modules,
    get_version,
    mark,
)


class Test_check:
    def test_all(self):
        assert _check(None, "") is False
        assert _check("load", "save") is False
        assert _check("load", "save::*") is False
        assert _check("save::txt", "load::*") is False
        assert _check("load::txt", "load::") is False

        assert _check("load::txt", "load::txt") is True
        assert _check("load::txt", "load::*") is True
        assert _check("load::image::png", "load::*") is True


class Test_mark:
    def test_internals(self):
        def f1():
            pass

        @mark("_test_group-1")
        def f2():
            pass

        @mark("_test_group-2")
        @mark("_test_group-1")
        def f3():
            pass

        assert not hasattr(f1, "__katalytic_marks__")
        assert f2.__katalytic_marks__ == ("_test_group-1",)
        assert f3.__katalytic_marks__ == ("_test_group-2", "_test_group-1")

    @pytest.mark.parametrize("group", [0, None, {}, True])
    def test_TypeError(self, group):
        with pytest.raises(TypeError):

            @mark(group)
            def f1():
                pass

    @pytest.mark.parametrize("group", ["", " ", " \n ", "\t \t", "no \t tabs", "no \n newlines"])
    def test_ValueError(self, group):
        with pytest.raises(ValueError):

            @mark(group)
            def f1():
                pass


class Test_get_functions_in_group:
    def test_empty(self):
        assert find_functions_marked_with("__not-used") == []
        assert find_functions_marked_with("__test_3") == []

    def test_pattern(self):
        found = find_functions_marked_with("__test_3*")
        found = [(name, groups) for name, _, groups in found]
        assert found == [("__test", ("__test_300",)), ("__test_2", ("__test_3::a", "__test_3::b"))]

    def test_exact(self):
        found = find_functions_marked_with("__test_1")
        found = [(name, groups) for name, _, groups in found]
        assert found == [("__test", ("__test_1",))]

        found = find_functions_marked_with("__test_2")
        found = [(name, groups) for name, _, groups in found]
        assert found == [("__test", ("__test_2",)), ("__test_2", ("__test_2",))]


class Test_get_katalytic_modules:
    def test_all(self):
        modules = get_katalytic_modules()
        modules = [m.__name__.replace(".__init__", "") for m in modules]
        assert "katalytic._pkg" in modules
        assert all(m.startswith("katalytic") for m in modules)


class Test_version:
    def test_is_ok(self):
        v, v_info = get_version("katalytic")

        assert v is not None
        assert v_info is not None
        assert v == __version__

        v2 = v.replace("+editable", ".editable")
        assert v2 == ".".join(str(i) for i in v_info)
