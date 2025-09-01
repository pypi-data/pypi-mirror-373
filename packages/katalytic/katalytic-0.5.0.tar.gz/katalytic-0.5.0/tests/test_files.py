import copy
import itertools
import shutil
import tempfile
import warnings
from pathlib import Path

import pytest

from katalytic._pkg import all_types_besides
from katalytic.data import as_dict_of_lists, as_list_of_lists, is_iterable, is_iterator
from katalytic.data.checks import dicts_share_key_order
from katalytic.files import (
    _get_all,
    _load_funcs,
    _save_funcs,
    clear_dir,
    copy_dir,
    copy_file,
    delete_dir,
    delete_file,
    get_all,
    get_dirs,
    get_files,
    get_unique_path,
    is_dir_empty,
    is_file_empty,
    load,
    load_csv,
    load_json,
    load_text,
    make_dir,
    move_dir,
    move_file,
    save,
    save_csv,
    save_json,
    save_text,
)


def _compute_all_mismatched_combos(group_dict):
    good_matches = group_dict.items()
    all_matches = itertools.product(group_dict.keys(), group_dict.values())
    bad_matches = (m for m in all_matches if m not in good_matches)
    return ((*m, group_dict[m[0]].__name__) for m in bad_matches)


def _create_seq_of_dicts():
    return [
        {"a": 1, "b": "x", "c": True, "d": -1.5, "e": True},
        {"a": 2, "b": None, "c": False, "d": 0.0, "e": "z"},
        {"a": None, "b": "y", "c": "", "d": None, "e": "w"},
    ]


def _create_seq_of_seq():
    return as_list_of_lists(_create_seq_of_dicts())


def _create_dict_of_seq():
    return as_dict_of_lists(_create_seq_of_dicts())


class TestGroup_save_and_load:
    class Test_warn_if_another_function_should_be_used:
        @pytest.mark.parametrize("ext, wrong_load, correct_load", _compute_all_mismatched_combos(_load_funcs))
        def test_using_the_wrong_loader_should_always_warn(self, ext, wrong_load, correct_load):
            # The warning should be triggered regardless of whether the file exists or not.
            with pytest.warns(UserWarning, match=f'Use "{correct_load}" for ".{ext}" files.'):
                try:
                    wrong_load(get_unique_path("{}." + ext))
                except Exception:
                    pass

        @pytest.mark.parametrize("ext, wrong_save, correct_save", _compute_all_mismatched_combos(_save_funcs))
        def test_using_the_wrong_saver_should_always_warn(self, ext, wrong_save, correct_save):
            with pytest.warns(UserWarning, match=f'Use "{correct_save}" for ".{ext}" files.'):
                try:
                    wrong_save("", get_unique_path("{}." + ext))
                except Exception:
                    pass

    class Test_csv:
        @pytest.mark.parametrize(
            "data",
            [
                [],
                [[]],
                {"a": []},
                {},
            ],
        )
        def test_empty_csv(self, data):
            p = get_unique_path("{}.csv")
            save_csv([], p)
            assert load_csv(p) == []

        def test_atomicity_interrupt(self):
            path = get_unique_path("{}.csv")
            data = [{"path": path}]

            save_csv.__katalytic_test_atomicity_interrupt__ = True
            save_csv(data, path)
            assert not Path(path).exists()

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            save_csv(data, path)
            assert load(path) == data

        def test_atomicity_race_condition_error(self):
            path = get_unique_path("{}.csv")
            data = [{"path": path}]

            save_csv.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(path).exists()
            with pytest.raises(FileExistsError):
                save_csv(data, path, exists="error")

            assert load(path) == [{"hello": "world", "race": "condition"}]

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_file(path)
            assert not Path(path).exists()
            save_csv(data, path, exists="error")
            assert load(path) == data

        def test_atomicity_race_condition_replace(self):
            path = get_unique_path("{}.csv")
            data = [{"path": path}]

            save_csv.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(path).exists()
            save_csv(data, path, exists="replace")
            assert load(path) == data

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_file(path)
            assert not Path(path).exists()
            save_csv(data, path, exists="replace")
            assert load(path) == data

        def test_atomicity_race_condition_skip(self):
            path = get_unique_path("{}.csv")
            data = [{"path": path}]

            save_csv.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(path).exists()
            save_csv(data, path, exists="skip")
            assert load(path) == [{"hello": "world", "race": "condition"}]

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_file(path)
            assert not Path(path).exists()
            save_csv(data, path, exists="skip")
            assert load(path) == data

        def test_default(self):
            path = get_unique_path("{}.csv")
            default = [{"a": 1, "b": 2}]
            assert load_csv(path, default=default) == default

        @pytest.mark.parametrize("mistake", [0, None, {}, True, "hello"])
        def test_precondition_exists(self, mistake):
            path = get_unique_path("{}.csv")
            with pytest.raises(ValueError):
                save_csv("", path, exists=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_make_dirs(self, mistake):
            path = get_unique_path("{}.csv")
            with pytest.raises(TypeError):
                save_csv("", path, make_dirs=mistake)

        def test_make_dirs_False(self):
            path = get_unique_path("{}/data.csv")
            with pytest.raises(FileNotFoundError):
                save_csv(_create_seq_of_dicts(), path, make_dirs=False)

            path = _setup_file("{}/data")
            with pytest.raises(NotADirectoryError):
                save_csv(_create_seq_of_dicts(), f"{path}/x.csv", make_dirs=False)

        def test_exists_error(self):
            path = _setup_file("{}.csv")
            with pytest.raises(FileExistsError):
                save_csv([], path, exists="error")

        def test_exists_replace(self):
            path = _setup_file("{}.csv")
            data = [{"a": 1, "b": 2}]
            save_csv(data, path, exists="replace")
            assert load_csv(path) == data

        def test_exists_skip(self):
            path = get_unique_path("{}.csv")
            data_before = [{"a": 1, "b": 2}]
            data_after = [{"x": 3, "y": 4}]

            save_csv(data_before, path)
            save_csv(data_after, path, exists="skip")
            assert load_csv(path) == data_before

        @pytest.mark.parametrize(
            "data",
            [
                _create_seq_of_seq(),
                _create_seq_of_dicts(),
                _create_dict_of_seq(),
            ],
        )
        def test_basic(self, data):
            expected = _create_seq_of_dicts()
            expected[0]["e"] = str(expected[0]["e"])
            expected[2]["c"] = None

            path = _setup_path()
            save_csv(data, path)
            assert load_csv(path) == expected

        def test_mixed_int_with_float(self):
            data = [{"a": 1, "b": 2.0}, {"a": 3.0, "b": 4}]
            expected = [{"a": 1.0, "b": 2}, {"a": 3.0, "b": 4.0}]

            path = _setup_path()
            save_csv(data, path)
            assert load_csv(path) == expected

        @pytest.mark.parametrize(
            "data",
            [
                [{"a": 1, "b": 2}, {"b": 4, "a": 3}],
                [{"b": 4, "a": 3}, {"a": 1, "b": 2}],
            ],
        )
        def test_mixed_column_order(self, data):
            path = _setup_path()
            save_csv(data, path)
            result = load_csv(path)

            assert result == data
            assert dicts_share_key_order(data[0], result[0])
            assert dicts_share_key_order(data[0], result[1])
            assert not dicts_share_key_order(data[0], data[1])

    class Test_json:
        def test_atomicity_interrupt(self):
            path = get_unique_path("{}.json")
            data = [{"path": path}]

            try:
                save_json.__katalytic_test_atomicity_interrupt__ = True
                save_json(data, path)
                assert not Path(path).exists()

                # make sure it's still working after the test
                # the atomicity flag is set back to False inside the function
                save_json(data, path)
                assert load_json(path) == data
            except:
                raise

        def test_atomicity_race_condition_error(self):
            path = get_unique_path("{}.json")
            data = [{"path": path}]

            try:
                save_json.__katalytic_test_atomicity_race_condition__ = True
                assert not Path(path).exists()
                with pytest.raises(FileExistsError):
                    save_json(data, path, exists="error")

                assert load(path) == [{"hello": "world", "race": "condition"}]

                # make sure it's still working after the test
                # the atomicity flag is set back to False inside the function
                delete_file(path)
                assert not Path(path).exists()
                save_json(data, path, exists="error")
                assert load(path) == data
            except:
                raise

        def test_atomicity_race_condition_replace(self):
            path = get_unique_path("{}.json")
            data = [{"path": path}]

            try:
                save_json.__katalytic_test_atomicity_race_condition__ = True
                assert not Path(path).exists()
                save_json(data, path, exists="replace")
                assert load(path) == data

                # make sure it's still working after the test
                # the atomicity flag is set back to False inside the function
                delete_file(path)
                assert not Path(path).exists()
                save_json(data, path, exists="replace")
                assert load(path) == data
            except:
                raise

        def test_atomicity_race_condition_skip(self):
            path = get_unique_path("{}.json")
            data = [{"path": path}]

            try:
                save_json.__katalytic_test_atomicity_race_condition__ = True
                assert not Path(path).exists()
                save_json(data, path, exists="skip")
                assert load(path) == [{"hello": "world", "race": "condition"}]

                # make sure it's still working after the test
                # the atomicity flag is set back to False inside the function
                delete_file(path)
                assert not Path(path).exists()
                save_json(data, path, exists="skip")
                assert load(path) == data
            except:
                raise

        def test_default(self):
            path = get_unique_path("{}.json")
            default = [{"a": 1, "b": 2}]
            assert load_json(path, default=default) == default

        @pytest.mark.parametrize("mistake", [0, None, {}, True, "hello"])
        def test_precondition_exists(self, mistake):
            path = get_unique_path("{}.json")
            with pytest.raises(ValueError):
                save_json([], path, exists=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_make_dirs(self, mistake):
            path = get_unique_path("{}.json")
            with pytest.raises(TypeError):
                save_json([], path, make_dirs=mistake)

        def test_make_dirs_False(self):
            path = get_unique_path("{}/data.json")
            with pytest.raises(FileNotFoundError):
                save_json(_create_seq_of_dicts(), path, make_dirs=False)

            path = _setup_file("{}/data")
            with pytest.raises(NotADirectoryError):
                save_json(_create_seq_of_dicts(), f"{path}/x.json", make_dirs=False)

        def test_exists_error(self):
            path = _setup_file("{}.json")
            with pytest.raises(FileExistsError):
                save_json([], path, exists="error")

        def test_exists_replace(self):
            path = _setup_file("{}.json")
            data = [{"a": 1, "b": 2}]
            save_json(data, path, exists="replace")
            assert load_json(path) == data

        def test_exists_skip(self):
            path = get_unique_path("{}.json")
            data_before = [{"a": 1, "b": 2}]
            data_after = [{"x": 3, "y": 4}]

            save_json(data_before, path)
            save_json(data_after, path, exists="skip")
            assert load_json(path) == data_before

        def test_indent_0(self):
            data = self.create_json_data()
            path = _setup_path()
            save_json(data, path, indent=0)
            assert load_json(path) == data

        def test_indent_positive(self):
            data = self.create_json_data()
            path = _setup_path()
            save_json(data, path, indent=4)
            assert load_json(path) == data

        def test_indent_negative(self):
            data = self.create_json_data()
            path = _setup_path()
            with pytest.raises(ValueError):
                save_json(data, path, indent=-1)

        def test_indent_as_float(self):
            data = self.create_json_data()
            path = _setup_path()

            save_json(data, path, indent=1.0)
            assert load_json(path) == data

        @pytest.mark.parametrize("mistake", all_types_besides("int"))
        def test_indent_of_wrong_type(self, mistake):
            data = self.create_json_data()
            path = _setup_path()
            with pytest.raises(TypeError):
                save_json(data, path, indent=mistake)

        def test_save_sort_keys(self):
            data = self.create_json_data()
            path = _setup_path()
            save_json(data, path, sort_keys=True)
            assert self.are_keys_sorted_recursive(load_json(path))

        def test_save_sort_keys_False(self):
            data = self.create_json_data()
            path = _setup_path()
            save_json(data, path, sort_keys=False)
            assert not self.are_keys_sorted_recursive(load_json(path))

        def are_keys_sorted_recursive(self, data):
            if isinstance(data, dict):
                if list(data.keys()) != sorted(data.keys()):
                    return False

                return all(self.are_keys_sorted_recursive(v) for v in data.values())
            elif is_iterable(data) and not isinstance(data, str):
                return all(self.are_keys_sorted_recursive(item) for item in data)
            else:
                return True

        @staticmethod
        def create_json_data():
            """The keys are shuffled on purpose."""
            return {
                "e": 0,
                "a": 1,
                "b": 2.0,
                "c": 3.5,
                "d": [{"y": None, "f": True, "g": {"x": "i", "j": [False]}}],
            }

    class Test_text:
        def test_atomicity_interrupt(self):
            path = get_unique_path("{}.txt")

            try:
                save_text.__katalytic_test_atomicity_interrupt__ = True
                save_text(path, path)
                assert not Path(path).exists()

                # make sure it's still working after the test
                # the atomicity flag is set back to False inside the function
                save_text(path, path)
                assert load(path) == path
            except:
                raise

        def test_atomicity_race_condition_error(self):
            path = get_unique_path("{}.txt")
            data = f"path = {path!r}"

            try:
                save_text.__katalytic_test_atomicity_race_condition__ = True
                assert not Path(path).exists()
                with pytest.raises(FileExistsError):
                    save_text(data, path, exists="error")

                assert load(path) == "race condition"

                # make sure it's still working after the test
                # the atomicity flag is set back to False inside the function
                delete_file(path)
                assert not Path(path).exists()
                save_text(data, path, exists="error")
                assert load(path) == data
            except:
                raise

        def test_atomicity_race_condition_replace(self):
            path = get_unique_path("{}.txt")
            data = f"path = {path!r}"

            try:
                save_text.__katalytic_test_atomicity_race_condition__ = True
                assert not Path(path).exists()
                save_text(data, path, exists="replace")
                assert load(path) == data

                # make sure it's still working after the test
                # the atomicity flag is set back to False inside the function
                delete_file(path)
                assert not Path(path).exists()
                save_text(data, path, exists="replace")
                assert load(path) == data
            except:
                raise

        def test_atomicity_race_condition_skip(self):
            path = get_unique_path("{}.txt")
            data = f"path = {path!r}"

            try:
                save_text.__katalytic_test_atomicity_race_condition__ = True
                assert not Path(path).exists()
                save_text(data, path, exists="skip")
                assert load(path) == "race condition"

                # make sure it's still working after the test
                # the atomicity flag is set back to False inside the function
                delete_file(path)
                assert not Path(path).exists()
                save_text(data, path, exists="skip")
                assert load(path) == data
            except:
                raise

        def test_default(self):
            path = get_unique_path("{}.txt")
            assert load_text(path, default="hello") == "hello"

        @pytest.mark.parametrize("mistake", [0, None, {}, True, "hello"])
        def test_precondition_exists(self, mistake):
            path = get_unique_path("{}.txt")
            with pytest.raises(ValueError):
                save_text("", path, exists=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_make_dirs(self, mistake):
            path = get_unique_path("{}.txt")
            with pytest.raises(TypeError):
                save_text("", path, make_dirs=mistake)

        def test_make_dirs_False(self):
            path = get_unique_path("{}/data.txt")
            with pytest.raises(FileNotFoundError):
                save_text("hello", path, make_dirs=False)

            path = _setup_file("{}/data")
            with pytest.raises(NotADirectoryError):
                save_text("hello", f"{path}/x.txt", make_dirs=False)

        def test_exists_error(self):
            path = _setup_file("{}.txt")
            with pytest.raises(FileExistsError):
                save_text("data", path, exists="error")

        def test_exists_replace(self):
            path = _setup_file("{}.txt")
            save_text("data", path, exists="replace")
            assert load_text(path) == "data"

        def test_exists_skip(self):
            path = get_unique_path("{}.txt")
            save_text("before", path)
            save_text("after", path, exists="skip")
            assert load_text(path) == "before"

        def test_basic(self):
            data = "some text\nwith newlines"
            path = _setup_path()
            save_text(data, path)
            assert load_text(path) == data

    class Test_universal_load_and_save:
        @pytest.mark.parametrize(
            "pattern, default",
            [
                ("{}.csv", _create_seq_of_dicts()),
                ("{}.json", _create_dict_of_seq()),
                ("{}.txt", "hello"),
            ],
        )
        def test_default(self, pattern, default):
            path = get_unique_path(pattern)
            assert load(path, default=default) == default

        def test_unknown(self):
            path = get_unique_path("{}.unknown")
            save("hello world", path)
            assert load(path) == "hello world"

        def test_txt(self):
            data = "Hello, World!\nThis is not a drill"
            path = _setup_path("{}.txt")
            save(data, path)

            assert load(path) == load_text(path) == data

        def test_csv(self):
            data = _create_seq_of_dicts()
            path = _setup_path("{}.CSV")
            save(data, path)

            expected_csv = copy.deepcopy(data)
            expected_csv[0]["e"] = str(expected_csv[0]["e"])
            expected_csv[2]["c"] = None

            expected_text = "\n".join(
                [
                    '"a","b","c","d","e"',
                    '"1","x","True","-1.5","True"',
                    '"2","","False","0.0","z"',
                    '"","y","","","w"',
                ]
            )

            assert load(path) == expected_csv

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                assert load_text(path).strip() == expected_text

        def test_json(self):
            data = {"a": 1, "b": [2, True, None, {}]}
            path = _setup_path("{}.json")
            save(data, path)

            expected_text = "\n".join(
                [
                    "{",
                    '    "a": 1,',
                    '    "b": [',
                    "        2,",
                    "        true,",
                    "        null,",
                    "        {}",
                    "    ]",
                    "}",
                ]
            )

            assert load(path) == data

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                assert load_text(path).strip() == expected_text


class TestGroup_copy:
    class Test_copy_dir:
        def test_atomicity_interrupt(self):
            src = _setup_tree()
            dest = get_unique_path()

            copy_dir.__katalytic_test_atomicity_interrupt__ = True
            copy_dir(src, dest)
            assert not Path(dest).exists()

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            copy_dir(src, dest)
            _check_tree(src, dest)

        def test_atomicity_race_condition_error(self):
            src = _setup_tree()
            dest = get_unique_path()

            copy_dir.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(dest).exists()
            with pytest.raises(FileExistsError):
                copy_dir(src, dest, dir_exists="error")

            assert is_dir_empty(dest)

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_dir(dest)
            copy_dir(src, dest, dir_exists="error")
            _check_tree(src, dest)

        def test_atomicity_race_condition_replace(self):
            src = _setup_tree()
            dest = get_unique_path()

            copy_dir.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(dest).exists()
            copy_dir(src, dest, dir_exists="replace")
            _check_tree(src, dest)

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_dir(dest)
            copy_dir(src, dest, dir_exists="replace")
            _check_tree(src, dest)

        def test_atomicity_race_condition_skip(self):
            src = _setup_tree()
            dest = get_unique_path()

            copy_dir.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(dest).exists()
            copy_dir(src, dest, dir_exists="skip")
            assert is_dir_empty(dest)

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_dir(dest)
            copy_dir(src, dest, dir_exists="skip")
            _check_tree(src, dest)

        def test_dest_is_dir(self):
            src = Path(_setup_tree("{}_src"))

            dest = Path(get_unique_path("{}_dest"))
            copy_dir(src, dest)
            _check_tree(src, dest / src.name)

            dest_2 = Path(get_unique_path("{}_dest_2"))
            copy_dir(src, dest_2 / src.name)
            _check_tree(src, dest_2 / src.name)

        def test_dest_is_file(self):
            with pytest.raises(NotADirectoryError):
                src = _setup_dir()
                dest = _setup_file()
                copy_dir(src, dest)

        def test_dir_exists_error(self):
            with pytest.raises(FileExistsError):
                src = _setup_tree()
                dest = _setup_tree()
                copy_dir(src, dest, dir_exists="error", file_exists="skip")

        def test_dir_exists_merge(self):
            src, src_file = _setup_dir_and_file()
            _setup_tree(src + "/{}")

            dest = _setup_tree()
            copy_dir(src, dest, dir_exists="merge", file_exists="skip")

            src_dirs = get_dirs(src, prefix=False, recursive=True)
            dest_dirs = get_dirs(dest, prefix=False, recursive=True)
            assert set(src_dirs).difference(dest_dirs) == set()
            assert set(dest_dirs).difference(src_dirs) != set()

        def test_dir_exists_replace(self):
            src, src_file = _setup_dir_and_file()
            dest = _setup_tree()
            copy_dir(src, dest, dir_exists="replace", file_exists="skip")

            src_tree = get_all(src, prefix=False, recursive=True)
            dest_tree = get_all(dest, prefix=False, recursive=True)
            assert src_tree == dest_tree

            src_tree = set(get_all(src, recursive=True))
            dest_tree = set(get_all(dest, recursive=True))
            pairs = {(fn, fn.replace(src, dest)) for fn in src_tree | dest_tree}
            pairs = {(Path(s), Path(d)) for s, d in pairs if Path(s).is_file()}
            assert all((s.read_text() == d.read_text()) for s, d in pairs)

        def test_dir_exists_skip(self):
            src, src_file = _setup_dir_and_file()
            dest, dest_file = _setup_dir_and_file()
            make_dir(f"{dest}/subdir")

            copy_dir(src, dest, dir_exists="skip", file_exists="replace")
            assert Path(dest_file).read_text() != Path(src_file).read_text()
            assert Path(f"{dest}/subdir").is_dir()

        def test_file_exists_error(self):
            with pytest.raises(FileExistsError):
                src = _setup_tree()
                dest = _setup_tree()
                copy_dir(src, dest, dir_exists="merge", file_exists="error")

        def test_file_exists_replace(self):
            src, src_file = _setup_dir_and_file()
            dest, dest_file = _setup_dir_and_file()

            copy_dir(src, dest, dir_exists="merge", file_exists="replace")
            assert Path(dest_file).read_text() == Path(src_file).read_text()

        def test_file_exists_skip(self):
            src, src_file = _setup_dir_and_file()
            dest, dest_file = _setup_dir_and_file()

            original = Path(dest_file).read_text()
            copy_dir(src, dest, dir_exists="merge", file_exists="skip")
            assert Path(dest_file).read_text() != Path(src_file).read_text()
            assert Path(dest_file).read_text() == original

        def test_make_dirs_false(self):
            with pytest.raises(FileNotFoundError):
                with tempfile.TemporaryDirectory() as d:
                    src = get_unique_path(d + "/{}_src")
                    dest = get_unique_path(d + "/{}_dest")
                    make_dir(src)
                    copy_dir(src, dest, make_dirs=False)

        def test_make_dirs_true(self):
            with tempfile.TemporaryDirectory() as d:
                src = _setup_tree()
                src_name = Path(src).name

                dest = get_unique_path(d + "/{}_dest")
                copy_dir(src, dest, make_dirs=True)
                _check_tree(src, f"{dest}/{src_name}")

                dest_2 = get_unique_path(d + "/{}_dest_2")
                copy_dir(src, f"{dest_2}/{src_name}", make_dirs=True)
                _check_tree(src, f"{dest_2}/{src_name}")

        def test_same_path(self):
            with pytest.raises(ValueError):
                src = _setup_dir()
                copy_dir(src, src)

        def test_src_is_file(self):
            with pytest.raises(NotADirectoryError):
                src = _setup_file()
                dest = get_unique_path("{}_new")
                copy_dir(src, dest)

        def test_src_is_missing(self):
            with pytest.raises(FileNotFoundError):
                src = get_unique_path()
                copy_dir(src, f"{src}_copy")

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_dest(self, mistake):
            with pytest.raises(TypeError):
                copy_dir("src", mistake)

        @pytest.mark.parametrize("mistake", [0, None, {}, True, "hello"])
        def test_precondition_dir_exists(self, mistake):
            with pytest.raises(ValueError):
                copy_dir("src", "dest", dir_exists=mistake)

        @pytest.mark.parametrize("mistake", [0, None, {}, "hello"])
        def test_precondition_file_exists(self, mistake):
            with pytest.raises(ValueError):
                copy_dir("src", "dest", file_exists=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_make_dirs(self, mistake):
            with pytest.raises(TypeError):
                src, dest = _setup_dir(n=2)
                copy_dir(src, dest, make_dirs=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_src(self, mistake):
            with pytest.raises(TypeError):
                copy_dir(mistake, "dest")

    class Test_copy_file:
        def test_atomicity_interrupt(self):
            src = _setup_file("{}.txt")
            dest = get_unique_path("{}.txt")

            copy_file.__katalytic_test_atomicity_interrupt__ = True
            copy_file(src, dest)
            assert not Path(dest).exists()

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            copy_file(src, dest)
            assert load(dest) == src

        def test_atomicity_race_condition_error(self):
            src = _setup_file("{}.txt")
            dest = get_unique_path("{}.txt")

            copy_file.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(dest).exists()
            with pytest.raises(FileExistsError):
                copy_file(src, dest, exists="error")

            assert load(dest) == "race condition"

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_file(dest)
            copy_file(src, dest, exists="error")
            assert load(dest) == src

        def test_atomicity_race_condition_replace(self):
            src = _setup_file("{}.txt")
            dest = get_unique_path("{}.txt")

            copy_file.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(dest).exists()
            copy_file(src, dest, exists="replace")
            assert load(dest) == src

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_file(dest)
            copy_file(src, dest, exists="replace")
            assert load(dest) == src

        def test_atomicity_race_condition_skip(self):
            src = _setup_file("{}.txt")
            dest = get_unique_path("{}.txt")

            copy_file.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(dest).exists()
            copy_file(src, dest, exists="skip")
            assert load(dest) == "race condition"

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_file(dest)
            copy_file(src, dest, exists="skip")
            assert load(dest) == src

        def test_dir(self):
            with pytest.raises(IsADirectoryError):
                src = _setup_dir()
                dest = get_unique_path()
                copy_file(src, dest)

        def test_exists_error(self):
            with pytest.raises(FileExistsError):
                src, dest = _setup_file(n=2)
                copy_file(src, dest, exists="error")

        def test_exists_replace(self):
            src, dest = _setup_file(n=2)
            copy_file(src, dest, exists="replace")

            text = Path(dest).read_text()
            assert text == Path(src).read_text()
            assert text != dest

        def test_exists_skip(self):
            src, dest = _setup_file(n=2)
            copy_file(src, dest, exists="skip")

            text = Path(dest).read_text()
            assert text != Path(src).read_text()
            assert text == dest

        def test_missing(self):
            dest = _setup_file()
            src = get_unique_path()
            with pytest.raises(FileNotFoundError):
                copy_file(src, dest)

        def test_ends_with_slash(self):
            src = _setup_file()
            root = get_unique_path()
            dest = root + "/1/2/3/"
            copy_file(src, dest)

        def test_make_dirs_false(self):
            with pytest.raises(FileNotFoundError):
                src = _setup_file()
                dest = get_unique_path("{}/a/b/c/")
                copy_file(src, dest, make_dirs=False)

        def test_make_dirs_true(self):
            src = _setup_file()
            dest = _setup_path()
            copy_file(src, dest, make_dirs=True)
            assert Path(dest).read_text() == src

        def test_same_path(self):
            with pytest.raises(ValueError):
                src = _setup_file()
                copy_file(src, src)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_src(self, mistake):
            with pytest.raises(TypeError):
                copy_file(mistake, "a")

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_dest(self, mistake):
            with pytest.raises(TypeError):
                copy_file("a", mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_make_dirs(self, mistake):
            with pytest.raises(TypeError):
                src, dest = _setup_file(n=2)
                copy_file(src, dest, make_dirs=mistake)

        @pytest.mark.parametrize("mistake", [0, None, {}, "hello"])
        def test_precondition_exists(self, mistake):
            src, dest = _setup_file(n=2)
            with pytest.raises(ValueError):
                copy_file(src, dest, exists=mistake)


class TestGroup_delete:
    class Test_delete_dir:
        def test_file(self):
            with pytest.raises(NotADirectoryError):
                path = _setup_file()
                delete_dir(path)

        def test_empty_dir(self):
            path = _setup_dir()
            delete_dir(path)
            assert not Path(path).exists()

        def test_missing_ok_false(self):
            with pytest.raises(FileNotFoundError):
                path = get_unique_path()
                delete_dir(path, missing_ok=False)

        def test_missing_ok_true(self):
            path = get_unique_path()
            delete_dir(path, missing_ok=True)
            assert not Path(path).exists()

        def test_non_empty_dir_skip(self):
            path, _ = _setup_dir_and_file()
            delete_dir(path, non_empty_dir="skip")
            assert Path(path).is_dir()

        def test_non_empty_dir_error(self):
            with pytest.raises(RuntimeError):
                path, _ = _setup_dir_and_file()
                delete_dir(path, non_empty_dir="error")

        def test_non_empty_dir_delete(self):
            path, _ = _setup_dir_and_file()
            delete_dir(path, non_empty_dir="delete")
            assert not Path(path).exists()

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_missing_ok(self, mistake):
            with pytest.raises(TypeError):
                delete_dir(get_unique_path(), missing_ok=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("str"))
        def test_precondition_non_empty_dir(self, mistake):
            with pytest.raises(ValueError):
                delete_dir(get_unique_path(), non_empty_dir=mistake)

        @pytest.mark.parametrize("mistake", [None, "", "."])
        def test_precondition_path_current_dir(self, mistake):
            with pytest.raises(ValueError):
                delete_dir(mistake)

        @pytest.mark.parametrize("mistake", all_types_besides(["none", "str", "path"]))
        def test_precondition_path_type(self, mistake):
            with pytest.raises(TypeError):
                delete_dir(mistake)

    class Test_delete_file:
        def test_dir(self):
            with pytest.raises(IsADirectoryError):
                path = _setup_dir()
                delete_file(path)

        def test_file(self):
            path = _setup_file()
            delete_file(path)
            assert not Path(path).exists()

        def test_missing_ok_false(self):
            with pytest.raises(FileNotFoundError):
                path = get_unique_path()
                delete_file(path, missing_ok=False)

        def test_missing_ok_true(self):
            path = get_unique_path()
            delete_file(path, missing_ok=True)
            assert not Path(path).exists()

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_path(self, mistake):
            with pytest.raises(TypeError):
                delete_file(mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_missing_ok(self, mistake):
            with pytest.raises(TypeError):
                delete_file(get_unique_path(), missing_ok=mistake)


class TestGroup_get:
    class Test_get_all:
        def test_prefix_false(self):
            path = _setup_tree()
            expected = ["1.txt", "a", "a/2.txt", "b", "b/3.txt", "b/c", "b/c/4.txt"]
            assert get_all(path, prefix=False, recursive=True) == expected

        def test_prefix_true(self):
            path = _setup_tree()
            expected = [
                f"{path}/1.txt",
                f"{path}/a",
                f"{path}/a/2.txt",
                f"{path}/b",
                f"{path}/b/3.txt",
                f"{path}/b/c",
                f"{path}/b/c/4.txt",
            ]
            assert get_all(path, prefix=True, recursive=True) == expected

        def test_path_is_file(self):
            with pytest.raises(NotADirectoryError):
                path = _setup_file()
                get_all(path)

        def test_path_is_missing(self):
            with pytest.raises(FileNotFoundError):
                get_all(get_unique_path())

        def test_iter(self):
            r = get_all("", iter_=True)
            assert is_iterator(r)

        def test_glob(self):
            path = _setup_tree_2()
            assert get_all(f"{path}/*/a/*") == [f"{path}/a/a/6.py", f"{path}/b/a/5.py"]

        def test_glob_recursive(self):
            path = _setup_tree_2()
            expected = sorted(map(str, Path(path).glob("**/a/*")))
            assert get_all(f"{path}/**/a/*") == expected
            assert get_all(f"{path}/*/a/*", recursive=True) == expected

            expected = sorted(map(str, Path(path).glob("**/a/**")))
            assert get_all(f"{path}/**/a/**") == expected
            assert get_all(f"{path}/**/a/**", recursive=True) == expected

        def test_only_dirs(self):
            path = _setup_tree()
            assert _get_all(path, only_dirs=True, prefix=False) == ["a", "b"]

        def test_only_files(self):
            path = _setup_tree()
            assert _get_all(path, only_files=True, prefix=False) == ["1.txt"]

        def test_only_conflict(self):
            with pytest.raises(ValueError):
                _get_all("", only_files=True, only_dirs=True)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_glob(self, mistake):
            with pytest.raises(TypeError):
                get_all("", glob=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_iter_(self, mistake):
            with pytest.raises(TypeError):
                get_all("", iter_=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_only_dirs(self, mistake):
            with pytest.raises(TypeError):
                _get_all("", only_dirs=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_only_files(self, mistake):
            with pytest.raises(TypeError):
                _get_all("", only_files=mistake)

        @pytest.mark.parametrize("mistake", [0, None, {}, True])
        def test_precondition_path(self, mistake):
            with pytest.raises(TypeError):
                get_all(mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_prefix(self, mistake):
            with pytest.raises(TypeError):
                get_all("", prefix=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_recursive(self, mistake):
            with pytest.raises(TypeError):
                get_all("", recursive=mistake)

        def test_recursive(self):
            path = _setup_tree()
            assert get_all(path, recursive=True) == [
                f"{path}/1.txt",
                f"{path}/a",
                f"{path}/a/2.txt",
                f"{path}/b",
                f"{path}/b/3.txt",
                f"{path}/b/c",
                f"{path}/b/c/4.txt",
            ]

        def test_sorted(self):
            path = _setup_tree()
            _ = _setup_tree(path + "/b/{}")
            assert get_all(path, iter_=False, recursive=True) == [
                f"{path}/1.txt",
                f"{path}/a",
                f"{path}/a/2.txt",
                f"{path}/b",
                f"{path}/b/1",
                f"{path}/b/1/1.txt",
                f"{path}/b/1/a",
                f"{path}/b/1/a/2.txt",
                f"{path}/b/1/b",
                f"{path}/b/1/b/3.txt",
                f"{path}/b/1/b/c",
                f"{path}/b/1/b/c/4.txt",
                f"{path}/b/3.txt",
                f"{path}/b/c",
                f"{path}/b/c/4.txt",
            ]

        def test_returns_same_type_as_input(self):
            path = _setup_tree()
            result = get_all(path, recursive=True)
            assert all(isinstance(p, str) for p in result)

            path = Path(_setup_tree())
            result = get_all(path, recursive=True)
            assert all(isinstance(p, Path) for p in result)

    class Test_get_dirs:
        def test_prefix_false(self):
            path = _setup_tree()
            assert get_dirs(path, prefix=False, recursive=True) == ["a", "b", "b/c"]

        def test_prefix_true(self):
            path = _setup_tree()
            expected = [f"{path}/a", f"{path}/b", f"{path}/b/c"]
            assert get_dirs(path, prefix=True, recursive=True) == expected

        def test_path_is_file(self):
            with pytest.raises(NotADirectoryError):
                path = _setup_file()
                get_dirs(path)

        def test_path_is_missing(self):
            with pytest.raises(FileNotFoundError):
                get_dirs(get_unique_path())

        def test_iter(self):
            r = get_dirs("", iter_=True)
            assert is_iterator(r)

        def test_glob(self):
            path = _setup_tree_2()
            assert get_dirs(f"{path}/*/a") == [f"{path}/a/a", f"{path}/b/a"]

        def test_glob_recursive(self):
            path = _setup_tree_2()
            expected = [f"{path}/a", f"{path}/a/a", f"{path}/b/a", f"{path}/b/c/a"]
            assert get_dirs(f"{path}/**/a") == expected
            assert get_dirs(f"{path}/*/a", recursive=True) == expected

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_prefix(self, mistake):
            with pytest.raises(TypeError):
                get_dirs("", prefix=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_glob(self, mistake):
            with pytest.raises(TypeError):
                get_dirs("", glob=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_iter_(self, mistake):
            with pytest.raises(TypeError):
                get_dirs("", iter_=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_path(self, mistake):
            with pytest.raises(TypeError):
                get_dirs(mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_recursive(self, mistake):
            with pytest.raises(TypeError):
                get_dirs("", recursive=mistake)

        def test_recursive(self):
            path = _setup_tree()
            assert get_dirs(path, recursive=True) == [
                f"{path}/a",
                f"{path}/b",
                f"{path}/b/c",
            ]

        def test_sorted(self):
            path = _setup_tree()
            _ = _setup_tree(path + "/b/{}")
            assert get_dirs(path, iter_=False, recursive=True) == [
                f"{path}/a",
                f"{path}/b",
                f"{path}/b/1",
                f"{path}/b/1/a",
                f"{path}/b/1/b",
                f"{path}/b/1/b/c",
                f"{path}/b/c",
            ]

        def test_returns_same_type_as_input(self):
            path = _setup_tree()
            result = get_dirs(path, recursive=True)
            assert all(isinstance(p, str) for p in result)

            path = Path(_setup_tree())
            result = get_dirs(path, recursive=True)
            assert all(isinstance(p, Path) for p in result)

    class Test_get_files:
        def test_prefix_false(self):
            path = _setup_tree()
            expected = ["1.txt", "a/2.txt", "b/3.txt", "b/c/4.txt"]
            assert get_files(path, prefix=False, recursive=True) == expected

        def test_prefix_true(self):
            path = _setup_tree()
            expected = [
                f"{path}/1.txt",
                f"{path}/a/2.txt",
                f"{path}/b/3.txt",
                f"{path}/b/c/4.txt",
            ]
            assert get_files(path, prefix=True, recursive=True) == expected

        def test_path_is_file(self):
            with pytest.raises(NotADirectoryError):
                path = _setup_file()
                get_files(path)

        def test_path_is_missing(self):
            with pytest.raises(FileNotFoundError):
                get_files(get_unique_path())

        def test_iter(self):
            r = get_files("", iter_=True)
            assert is_iterator(r)

        def test_glob(self):
            path = _setup_tree_2()
            assert get_files(f"{path}/*.py") == [f"{path}/1.py"]

        def test_glob_recursive(self):
            path = _setup_tree_2()
            expected = [
                f"{path}/1.py",
                f"{path}/a/2.py",
                f"{path}/a/a/6.py",
                f"{path}/b/a/5.py",
            ]
            assert get_files(f"{path}/**/*.py") == expected

        def test_only_conflict(self):
            with pytest.raises(ValueError):
                _get_all("", only_files=True, only_dirs=True)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_prefix(self, mistake):
            with pytest.raises(TypeError):
                get_files("", prefix=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_glob(self, mistake):
            with pytest.raises(TypeError):
                get_files("", glob=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_iter_(self, mistake):
            with pytest.raises(TypeError):
                get_files("", iter_=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_path(self, mistake):
            with pytest.raises(TypeError):
                get_files(mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_recursive(self, mistake):
            with pytest.raises(TypeError):
                get_files("", recursive=mistake)

        def test_recursive(self):
            path = _setup_tree()
            assert get_files(path, recursive=True) == [
                f"{path}/1.txt",
                f"{path}/a/2.txt",
                f"{path}/b/3.txt",
                f"{path}/b/c/4.txt",
            ]

        def test_sorted(self):
            path = _setup_tree()
            _ = _setup_tree(path + "/b/{}")
            assert get_files(path, iter_=False, recursive=True) == [
                f"{path}/1.txt",
                f"{path}/a/2.txt",
                f"{path}/b/1/1.txt",
                f"{path}/b/1/a/2.txt",
                f"{path}/b/1/b/3.txt",
                f"{path}/b/1/b/c/4.txt",
                f"{path}/b/3.txt",
                f"{path}/b/c/4.txt",
            ]

        def test_returns_same_type_as_input(self):
            path = _setup_tree()
            result = get_files(path, recursive=True)
            assert all(isinstance(p, str) for p in result)

            path = Path(_setup_tree())
            result = get_files(path, recursive=True)
            assert all(isinstance(p, Path) for p in result)


class TestGroup_misc_dir:
    class Test_clear_dir:
        def test_clear_empty(self):
            path = _setup_dir()
            clear_dir(path)
            assert list(Path(path).iterdir()) == []

        def test_clear_non_empty(self):
            path, _ = _setup_dir_and_file()
            clear_dir(path)
            assert list(Path(path).iterdir()) == []

        def test_create_missing_false(self):
            d = get_unique_path()
            shutil.rmtree(d, ignore_errors=True)
            clear_dir(d, create_missing=False)
            assert not Path(d).exists()

        def test_create_missing_true(self):
            path = get_unique_path()
            clear_dir(path, create_missing=True)
            assert is_dir_empty(path)

        def test_is_file(self):
            with pytest.raises(NotADirectoryError):
                file = _setup_file()
                clear_dir(file)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_create_missing(self, mistake):
            path = get_unique_path()
            with pytest.raises(TypeError):
                clear_dir(path, create_missing=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_path(self, mistake):
            with pytest.raises(TypeError):
                clear_dir(mistake)

    class Test_is_dir_empty:
        def test_empty(self):
            path = _setup_dir()
            assert is_dir_empty(path)

        def test_is_file(self):
            with pytest.raises(NotADirectoryError):
                path = _setup_file()
                is_dir_empty(path)

        def test_missing_error(self):
            with pytest.raises(FileNotFoundError):
                is_dir_empty(get_unique_path(), missing="error")

        def test_missing_false(self):
            path = get_unique_path()
            assert is_dir_empty(path, missing=False) is False

        def test_missing_true(self):
            path = get_unique_path()
            assert is_dir_empty(path, missing=True) is True

        def test_non_empty(self):
            path, _ = _setup_dir_and_file()
            assert not is_dir_empty(path)

        @pytest.mark.parametrize("mistake", [[], "", 0, None])
        def test_precondition_missing(self, mistake):
            with pytest.raises(ValueError):
                path = get_unique_path()
                is_dir_empty(path, missing=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_path(self, mistake):
            with pytest.raises(TypeError):
                is_dir_empty(mistake)

    class Test_mkdir:
        def test_create(self):
            path = _setup_dir()
            assert Path(path).is_dir()

            path = _setup_dir("a/{}/b")
            assert Path(path).is_dir()

        def test_exists_error(self):
            with pytest.raises(FileExistsError):
                path = _setup_dir()
                make_dir(path, exists_ok=False)

        def test_exists_ok(self):
            path = _setup_dir()
            make_dir(path, exists_ok=True)
            assert Path(path).is_dir()

        def test_idempotency(self):
            path = _setup_dir()
            make_dir(path)
            assert Path(path).is_dir()

        def test_is_file(self):
            with pytest.raises(NotADirectoryError):
                path = _setup_file()
                make_dir(path)

        def test_no_parents(self):
            with pytest.raises(FileNotFoundError):
                d = get_unique_path("parent/{}/child")
                make_dir(d, create_parents=False)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_create_parents(self, mistake):
            with pytest.raises(TypeError):
                make_dir(get_unique_path(), create_parents=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_exists_ok(self, mistake):
            with pytest.raises(TypeError):
                make_dir(get_unique_path(), exists_ok=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_path(self, mistake):
            with pytest.raises(TypeError):
                make_dir(mistake)


class TestGroup_misc_file:
    class Test_is_file_empty:
        def test_is_dir(self):
            with pytest.raises(IsADirectoryError):
                is_file_empty(_setup_dir())

        def test_missing_error(self):
            with pytest.raises(FileNotFoundError):
                is_file_empty(get_unique_path(), missing="error")

        def test_missing_false(self):
            path = get_unique_path()
            assert is_file_empty(path, missing=False) is False

        def test_missing_true(self):
            path = get_unique_path()
            assert is_file_empty(path, missing=True) is True

        def test_empty(self):
            path = get_unique_path()
            Path(path).touch()
            assert is_file_empty(path)

        def test_non_empty(self):
            path = get_unique_path()
            Path(path).write_text("hello")
            assert not is_file_empty(path)

        @pytest.mark.parametrize("mistake", [[], "", 0, None])
        def test_precondition_missing(self, mistake):
            with pytest.raises(ValueError):
                path = get_unique_path()
                is_file_empty(path, missing=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_path(self, mistake):
            with pytest.raises(TypeError):
                is_file_empty(mistake)


class TestGroup_move:
    class Test_move_dir:
        def test_dest_is_dir(self):
            src = Path(_setup_tree("{}_src"))
            src_copy = Path(get_unique_path("{}_src_copy"))
            copy_dir(src, src_copy)

            dest = get_unique_path("{}_dest")
            move_dir(src, dest)
            _check_tree(src_copy, dest)
            assert not src.exists()

            src = Path(_setup_tree("{}_src"))
            src_copy = Path(get_unique_path("{}_src_copy"))
            copy_dir(src, src_copy)

            dest = Path(get_unique_path("{}_dest"))
            move_dir(src, dest / src.name)
            _check_tree(src_copy / src.name, dest / src.name)
            assert not src.exists()

        def test_dest_is_file(self):
            with pytest.raises(NotADirectoryError):
                src = _setup_dir()
                dest = _setup_file()
                move_dir(src, dest)

        def test_dir_exists_error(self):
            with pytest.raises(FileExistsError):
                src = _setup_tree()
                dest = _setup_tree()
                move_dir(src, dest, dir_exists="error", file_exists="skip")

        def test_dir_exists_merge(self):
            src, src_file = _setup_dir_and_file()
            _setup_tree(src + "/{}")
            src_dirs = get_dirs(src, prefix=False, recursive=True)

            dest = _setup_tree()
            move_dir(src, dest, dir_exists="merge", file_exists="skip")

            dest_dirs = get_dirs(dest, prefix=False, recursive=True)
            assert set(src_dirs).difference(dest_dirs) == set()
            assert set(dest_dirs).difference(src_dirs) != set()

        def test_dir_exists_replace(self):
            src, src_file = _setup_dir_and_file()
            src_tree = get_all(src, prefix=False, recursive=True)
            src_tree_2 = set(get_all(src, recursive=True))

            dest = _setup_tree()
            move_dir(src, dest, dir_exists="replace", file_exists="skip")

            dest_tree = get_all(dest, prefix=False, recursive=True)
            assert src_tree == dest_tree

            dest_tree = set(get_all(dest, recursive=True))
            pairs = {(fn, fn.replace(src, dest)) for fn in src_tree_2 | dest_tree}
            pairs = {(Path(s), Path(d)) for s, d in pairs if Path(s).is_file()}
            assert all((s.read_text() == d.read_text()) for s, d in pairs)

        def test_dir_exists_skip(self):
            src, src_file = _setup_dir_and_file()
            dest, dest_file = _setup_dir_and_file()
            make_dir(f"{dest}/subdir")

            move_dir(src, dest, dir_exists="skip", file_exists="replace")
            assert Path(dest_file).read_text() != Path(src_file).read_text()
            assert Path(f"{dest}/subdir").is_dir()

        def test_file_exists_error(self):
            with pytest.raises(FileExistsError):
                src = _setup_tree()
                dest = _setup_tree()
                move_dir(src, dest, dir_exists="merge", file_exists="error")

        def test_file_exists_replace(self):
            src, src_file = _setup_dir_and_file()
            dest, dest_file = _setup_dir_and_file()
            src_file_text = Path(src_file).read_text()

            move_dir(src, dest, dir_exists="merge", file_exists="replace")
            assert Path(dest_file).read_text() == src_file_text

        def test_file_exists_skip(self):
            src, src_file = _setup_dir_and_file()
            dest, dest_file = _setup_dir_and_file()

            src_file_text = Path(src_file).read_text()
            original = Path(dest_file).read_text()

            move_dir(src, dest, dir_exists="merge", file_exists="skip")
            assert Path(dest_file).read_text() != src_file_text
            assert Path(dest_file).read_text() == original

        def test_make_dirs_false(self):
            with pytest.raises(FileNotFoundError):
                with tempfile.TemporaryDirectory() as d:
                    src = get_unique_path(d + "/{}_src")
                    dest = get_unique_path(d + "/{}_dest")
                    make_dir(src)
                    move_dir(src, dest, make_dirs=False)

        def test_make_dirs_true(self):
            with tempfile.TemporaryDirectory() as d:
                src = _setup_tree()
                src_name = Path(src).name
                src_copy = Path(get_unique_path("{}_src_copy"))
                copy_dir(src, src_copy)

                dest = get_unique_path(d + "/{}_dest")
                move_dir(src, dest, make_dirs=True)
                _check_tree(src_copy / src_name, f"{dest}/{src_name}")

                src = _setup_tree()
                src_name = Path(src).name
                src_copy = Path(get_unique_path("{}_src_copy"))
                copy_dir(src, src_copy)

                dest_2 = get_unique_path(d + "/{}_dest_2")
                move_dir(src, f"{dest_2}/{src_name}", make_dirs=True)
                _check_tree(src_copy / src_name, f"{dest_2}/{src_name}")

        def test_same_path(self):
            with pytest.raises(ValueError):
                src = _setup_dir()
                move_dir(src, src)

        def test_src_is_file(self):
            with pytest.raises(NotADirectoryError):
                src = _setup_file()
                dest = get_unique_path("{}_new")
                move_dir(src, dest)

        def test_src_is_missing(self):
            with pytest.raises(FileNotFoundError):
                src = get_unique_path()
                move_dir(src, f"{src}_copy")

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_dest(self, mistake):
            with pytest.raises(TypeError):
                move_dir("src", mistake)

        @pytest.mark.parametrize("mistake", [0, None, {}, True, "hello"])
        def test_precondition_dir_exists(self, mistake):
            with pytest.raises(ValueError):
                move_dir("src", "dest", dir_exists=mistake)

        @pytest.mark.parametrize("mistake", [0, None, {}, "hello"])
        def test_precondition_file_exists(self, mistake):
            with pytest.raises(ValueError):
                move_dir("src", "dest", file_exists=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_make_dirs(self, mistake):
            with pytest.raises(TypeError):
                src, dest = _setup_dir(n=2)
                move_dir(src, dest, make_dirs=mistake)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_src(self, mistake):
            with pytest.raises(TypeError):
                move_dir(mistake, "dest")

    class Test_move_file:
        def test_atomicity_interrupt(self):
            src = _setup_file("{}.txt")
            dest = get_unique_path("{}.txt")

            move_file.__katalytic_test_atomicity_interrupt__ = True
            move_file(src, dest)
            assert not Path(dest).exists()

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            move_file(src, dest)
            assert load(dest) == src

        def test_atomicity_race_condition_error(self):
            src = _setup_file("{}.txt")
            dest = get_unique_path("{}.txt")

            move_file.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(dest).exists()
            with pytest.raises(FileExistsError):
                move_file(src, dest, exists="error")

            assert load(dest) == "race condition"

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_file(dest)
            move_file(src, dest, exists="error")
            assert load(dest) == src

        def test_atomicity_race_condition_replace(self):
            src = _setup_file("{}.txt")
            dest = get_unique_path("{}.txt")

            move_file.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(dest).exists()
            move_file(src, dest, exists="replace")
            assert load(dest) == src

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_file(dest)
            src = _setup_file("{}.txt")
            move_file(src, dest, exists="replace")
            assert load(dest) == src

        def test_atomicity_race_condition_skip(self):
            src = _setup_file("{}.txt")
            dest = get_unique_path("{}.txt")

            move_file.__katalytic_test_atomicity_race_condition__ = True
            assert not Path(dest).exists()
            move_file(src, dest, exists="skip")
            assert load(dest) == "race condition"

            # make sure it's still working after the test
            # the atomicity flag is set back to False inside the function
            delete_file(dest)
            src = _setup_file("{}.txt")
            move_file(src, dest, exists="skip")
            assert load(dest) == src

        def test_dir(self):
            with pytest.raises(IsADirectoryError):
                src = _setup_dir()
                dest = get_unique_path()
                move_file(src, dest)

        def test_missing(self):
            with pytest.raises(FileNotFoundError):
                src = get_unique_path()
                dest = get_unique_path()
                move_file(src, dest)

        def test_exists_error(self):
            with pytest.raises(FileExistsError):
                src, dest = _setup_file(n=2)
                move_file(src, dest, exists="error")

        def test_exists_replace(self):
            src, dest = _setup_file(n=2)
            expected_text = Path(src).read_text()
            move_file(src, dest, exists="replace")

            text = Path(dest).read_text()
            assert text == expected_text
            assert text != dest
            assert not Path(src).exists()

        def test_exists_skip(self):
            src, dest = _setup_file(n=2)
            move_file(src, dest, exists="skip")

            text = Path(dest).read_text()
            assert text != Path(src).read_text()
            assert text == dest
            assert Path(src).exists()

        def test_make_dirs_false(self):
            with pytest.raises(FileNotFoundError):
                src = _setup_file()
                dest = get_unique_path("{}/a/b/c/")
                move_file(src, dest, make_dirs=False)

        def test_make_dirs_true(self):
            src = _setup_file()
            dest = _setup_path()
            move_file(src, dest, make_dirs=True)
            assert Path(dest).read_text() == src
            assert not Path(src).exists()

        def test_same_path(self):
            with pytest.raises(ValueError):
                src = _setup_file()
                move_file(src, src)

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_src(self, mistake):
            with pytest.raises(TypeError):
                move_file(mistake, "a")

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_precondition_dest(self, mistake):
            with pytest.raises(TypeError):
                move_file("a", mistake)

        @pytest.mark.parametrize("mistake", all_types_besides("booleans"))
        def test_precondition_make_dirs(self, mistake):
            with pytest.raises(TypeError):
                src, dest = _setup_file(n=2)
                move_file(src, dest, make_dirs=mistake)

        @pytest.mark.parametrize("mistake", [0, None, {}, "hello"])
        def test_precondition_exists(self, mistake):
            src, dest = _setup_file(n=2)
            with pytest.raises(ValueError):
                move_file(src, dest, exists=mistake)


class TestGroup_paths:
    class Test_get_unique_path:
        def test_consecutive_values(self):
            root = Path(_setup_dir())
            for i in range(1, 11):
                file = get_unique_path(root / "{}")
                assert file == Path(f"{root}/{i}")
                Path(file).touch()

        @pytest.mark.parametrize("mistake", all_types_besides(["str", "path"]))
        def test_invalid_pattern_type(self, mistake):
            with pytest.raises(TypeError):
                get_unique_path(mistake)

        @pytest.mark.parametrize("mistake", ["", "{0}", "{a}", "{:f}"])
        def test_invalid_placeholder(self, mistake):
            with pytest.raises(ValueError):
                get_unique_path(mistake)

        def test_keeps_slash_at_the_end(self):
            assert get_unique_path("{}/").endswith("/")

        def test_returns_same_type_as_input(self):
            assert isinstance(get_unique_path("{}"), str)
            assert isinstance(get_unique_path(Path("{}")), Path)

        @pytest.mark.parametrize("mistake", ["hello_{}", "{}", "./{}", "/a/{}", "/{}/a", "{:06d}"])
        def test_not_exists(self, mistake):
            path = get_unique_path(mistake)
            assert not Path(path).exists()


def _check_tree(src, dest):
    for src_item in Path(src).iterdir():
        dest_item = str(src_item).replace(str(src), str(dest))
        dest_item = Path(dest_item)

        if src_item.is_dir():
            assert dest_item.is_dir()
            _check_tree(src_item, dest_item)
        else:
            assert dest_item.is_file()


def _setup_tree(path=None):
    path = _setup_path(path)

    for d in [path, f"{path}/a", f"{path}/b", f"{path}/b/c"]:
        _setup_dir(d)

    for f in [
        f"{path}/1.txt",
        f"{path}/a/2.txt",
        f"{path}/b/3.txt",
        f"{path}/b/c/4.txt",
    ]:
        _setup_file(f)

    return str(path)


def _setup_tree_2(path=None):
    path = _setup_tree(path)

    make_dir(f"{path}/a/a")
    make_dir(f"{path}/b/a")
    make_dir(f"{path}/b/c/a")
    make_dir(f"{path}/b/c/a/d")

    Path(f"{path}/1.py").touch()
    Path(f"{path}/a/2.py").touch()
    Path(f"{path}/b/a/5.py").touch()
    Path(f"{path}/a/a/6.py").touch()

    return path


def _setup_dir_and_file(path_dir=None, filename=None):
    if filename is None:
        filename = "file"

    dir_ = _setup_dir(path_dir)
    file = _setup_file(Path(dir_) / filename)
    return dir_, file


def _setup_file(path=None, n=1):
    files = []
    for _ in range(n):
        file = _setup_path(path)
        make_dir(Path(file).parent)
        Path(file).write_text(file)

        files.append(file)

    if n == 1:
        return files[0]
    else:
        return files


def _setup_dir(path=None, n=1):
    dirs = []
    for _ in range(n):
        path = _setup_path(path)
        make_dir(path)
        dirs.append(path)

    if n == 1:
        return dirs[0]
    else:
        return dirs


def _setup_path(path=None):
    if path is None:
        return get_unique_path()
    elif "{}" in str(path):
        return get_unique_path(path)
    else:
        return str(path)
