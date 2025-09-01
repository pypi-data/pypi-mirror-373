import csv
import errno
import itertools
import re
import shutil
import tempfile
import warnings
from pathlib import Path

try:
    # use a faster json package by default
    import ujson as json
except ImportError:  # pragma: no cover -- can't test both branches in the same run
    # fallback to the stdlib version
    import json

from katalytic._pkg import (
    _UNDEFINED,
    KatalyticInterrupt,
    find_functions_marked_with,
    mark,
)
from katalytic.data import as_list_of_lists, is_none_of, sort_dict_by_keys
from katalytic.data.checks import is_pathlike
from katalytic.meta import extract_call_stack_info


@mark("load::csv")
def load_csv(path, *, default=_UNDEFINED, encoding="utf-8"):
    """Load data from a CSV file and return it as a list of dictionaries. It will guess
    the data type of each column based on its values.

    Args:
        path (str):
            The path to the CSV file.
        default (Any):
            The default value to return if the specified file path does not exist.
        encoding (str, optional):
            The encoding of the CSV file. Defaults to 'utf-8'.

    Returns:
        list:
            A list of dictionaries, where each dictionary corresponds to a row
            and the keys are the column headers. The values are converted to
            appropriate data types based on their contents, with empty strings
            converted to None.
    """
    # Using the wrong extension would return default or raise an error even if the file exists.
    # Trigger the warning before that happens, to provide a hint to the user about the real problem
    _warn_if_another_function_should_be_used(path, _load_funcs)
    if not Path(path).exists() and default is not _UNDEFINED:
        return default

    with open(path, encoding=encoding) as f:
        peek = f.read(1024)
        if peek.strip() == "":
            return []

        dialect = csv.Sniffer().sniff(peek)
        f.seek(0)

        reader = csv.reader(f, dialect)
        header = next(reader)
        data = [dict(zip(header, row, strict=False)) for row in reader]

    for col in header:
        t = _guess_type(col, data)

        for i, row in enumerate(data):
            # The csv reader reads missing values as empty strings.
            # Convert all empty strings to None even though they might
            # be actual empty strings
            if row[col] in ("None", ""):
                data[i][col] = None

        if t == "bool":
            for i, row in enumerate(data):
                if row[col] == "True":
                    data[i][col] = True
                elif row[col] == "False":
                    data[i][col] = False
        elif t == "float":
            for i, row in enumerate(data):
                if row[col] is not None:
                    data[i][col] = float(row[col])
        elif t == "int":
            for i, row in enumerate(data):
                if row[col] is not None:
                    data[i][col] = int(row[col])

    return data


def _guess_type(col, data):
    """Guesses the data type of a column in a dataset based on its values.

    Args:
        col (str):
            The column name to guess the data type for.
        data (list of dict):
            The dataset in the form of a list of dictionaries, where each dictionary
            represents a row and with the header as keys.

    Returns:
        str:
            The guessed data type of the column. Possible values are 'bool', 'float',
            'int', or 'str'.
    """
    is_bool = True
    is_float = False
    is_number = True

    for i, row in enumerate(data):
        v = row[col]
        if not (is_number or is_bool):
            return "str"

        if v in ("None", ""):
            continue

        if v in ("True", "False"):
            is_number = False
            continue
        else:
            is_bool = False

        if not re.search(r"^-?\d+(\.\d+)?$", v):
            is_number = False
        elif "." in v:
            is_float = True

    if is_bool:
        return "bool"
    elif is_number:
        if is_float:
            return "float"
        else:
            return "int"
    else:
        return "str"


@mark("save::csv")
def save_csv(data, path, *, encoding="utf-8", exists="replace", make_dirs=True):
    """Save data to a CSV file.

    Args:
        data (iterable):
            The data to be saved. It can be any of the following formats:
            a dict of lists, a list of lists, a list of dicts
        path (str):
            The path to the CSV file.
        encoding (str, optional):
            The encoding of the CSV file. Defaults to 'utf-8'.
        exists (str, optional):
            Specifies the behavior if the destination file already exists. Defaults to 'replace'.

            - 'error': Raise an error.
            - 'replace': Replace the existing file.
            - 'skip': Skip copying the file.
        make_dirs (bool or str, optional):
            Specifies whether to create the destination directory if it doesn't exist. Defaults to True.

            - True: Create the directory if it doesn't exist.
            - False: Raise an error if the destination directory doesn't exist.

    Returns:
        None

    Raises:
        IOError:
            If there is an error while saving the CSV file.
    """
    if exists not in ("error", "replace", "skip"):
        raise ValueError(f'<exists> expects "error", "replace", or "skip". Got {exists!r}')
    elif not isinstance(make_dirs, bool):
        raise TypeError(f"<make_dirs> expects False, or True. Got {make_dirs!r}")

    # optimization: trigger the warning only if the parameter preconditions are valid
    _warn_if_another_function_should_be_used(path, _save_funcs)

    # optimization: run the checks before starting to save the file, just in case the
    # path exists already when the function is called. This will ensure we don't
    # waste time saving the file only to raise an error or skip it when we do the same checks
    # right at the end of the function
    if Path(path).exists():
        if exists == "error":
            raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(path)!r}")
        elif exists == "replace":
            pass  # continue executing
        elif exists == "skip":
            return

    dest_dir = Path(path).parent
    if make_dirs:
        make_dir(dest_dir, create_parents=True, exists_ok=True)
    elif not dest_dir.exists():
        raise FileNotFoundError(f"[Errno {errno.ENOENT}] Directory does not exist: {str(dest_dir)!r}")
    elif not dest_dir.is_dir():
        raise NotADirectoryError(f"[Errno {errno.ENOTDIR}] Not a directory: {str(dest_dir)!r}")

    data = as_list_of_lists(data)

    try:
        tmp_path = f"{path}.part"
        with open(tmp_path, "w", newline="", encoding=encoding) as f:
            csv.writer(f, quoting=csv.QUOTE_ALL).writerows(data)

        # You could move the atomicity code higher in the function, but then
        # you wouldn't be testing the function for the worst case scenario
        if save_csv.__katalytic_test_atomicity_race_condition__:
            save_csv.__katalytic_test_atomicity_race_condition__ = False

            # I can't use save_csv([{"hello": "world", "race": "condition"}], path) directly
            # It would replace the tmp_path = f'{path}.part' created above
            # and then move it to the target `path`. This function wouldn't
            # be able to find the tmp_path anymore and will throw an error
            # at the end of the function: `Path(tmp_path).rename(path)`
            tmp_path_2 = path.replace(".csv", ".2.csv")
            save_csv([{"hello": "world", "race": "condition"}], tmp_path_2)
            Path(tmp_path_2).rename(path)

        # Checking these conditions again to make the function
        # as robust as possible against race conditions
        if Path(path).exists():
            if exists == "error":
                raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(path)!r}")
            elif exists == "replace":
                pass  # continue executing
            elif exists == "skip":
                return

        if save_csv.__katalytic_test_atomicity_interrupt__:
            save_csv.__katalytic_test_atomicity_interrupt__ = False
            raise KatalyticInterrupt("Testing atomicity ...")

        # The rename is atomic on POSIX systems, but not guaranteed on Windows
        Path(tmp_path).rename(path)
    except BaseException as e:
        if not isinstance(e, KatalyticInterrupt):
            raise


@mark("load::json")
def load_json(path, *, default=_UNDEFINED, encoding="utf-8"):
    """Load data from a JSON file.

    Args:
        path (str):
            The path to the JSON file.
        default (Any):
            The default value to return if the specified file path does not exist.
        encoding (str, optional):
            The encoding of the JSON file. Defaults to 'utf-8'.

    Returns:
        dict or list:
            The loaded JSON data as a dictionary or list, depending on the JSON structure.

    Raises:
        FileNotFoundError:
            If the specified file path does not exist.
        IOError:
            If there is an error while reading the JSON file.
        JSONDecodeError:
            If the JSON file is not properly formatted and cannot be decoded.
    """
    # Using the wrong extension would return default or raise an error even if the file exists.
    # Trigger the warning before that happens, to provide a hint to the user about the real problem
    _warn_if_another_function_should_be_used(path, _load_funcs)
    if not Path(path).exists() and default is not _UNDEFINED:
        return default

    with open(path, encoding=encoding) as f:
        return json.load(f)


@mark("save::json")
def save_json(data, path, *, encoding="utf-8", exists="replace", indent=4, make_dirs=True, sort_keys=True):
    """Save data to a JSON file.

    Args:
        data (dict or list):
            The data to be saved as JSON. It should be a dictionary or a list.
        path (str):
            The path to the output JSON file.
        encoding (str, optional):
            The encoding of the JSON file. Defaults to 'utf-8'.
        exists (str, optional):
            Specifies the behavior if the destination file already exists. Defaults to 'replace'.

            - 'error': Raise an error.
            - 'replace': Replace the existing file.
            - 'skip': Skip copying the file.
        indent (int or None, optional):
            The number of spaces used for indentation in the output JSON file.
            If indent is a non-negative integer, it specifies the number of spaces
            for each indentation level. If indent is None or not provided, the output
            JSON will be compact without any indentation. Defaults to 4.
        make_dirs (bool or str, optional):
            Specifies whether to create the destination directory if it doesn't exist. Defaults to True.

            - True: Create the directory if it doesn't exist.
            - False: Raise an error if the destination directory doesn't exist.
        sort_keys (bool, optional):
            Specifies whether the keys in the output JSON should be sorted. Defaults to True.

    Returns:
        None

    Raises:
        TypeError:
            If <indent> is not an integer or a positive integer.
        ValueError:
            If <indent> is a negative integer.
        IOError:
            If there is an error while saving the JSON file.
    """
    if isinstance(indent, float) and indent.is_integer():
        indent = int(indent)
    elif not isinstance(indent, int) or isinstance(indent, bool):
        raise TypeError(f"<indent> expects a positive integer. Got {indent!r}")
    elif indent < 0:
        raise ValueError(f"<indent> expects a positive integer. Got {indent!r}")
    elif exists not in ("error", "replace", "skip"):
        raise ValueError(f'<exists> expects "error", "replace", or "skip". Got {exists!r}')
    elif not isinstance(make_dirs, bool):
        raise TypeError(f"<make_dirs> expects False, or True. Got {make_dirs!r}")

    # optimization: trigger the warning only if the preconditions are valid
    _warn_if_another_function_should_be_used(path, _save_funcs)
    if Path(path).exists():
        if exists == "error":
            raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(path)!r}")
        elif exists == "replace":
            pass  # continue executing
        elif exists == "skip":
            return

    dest_dir = Path(path).parent
    if make_dirs:
        make_dir(dest_dir, create_parents=True, exists_ok=True)
    elif not dest_dir.exists():
        raise FileNotFoundError(f"[Errno {errno.ENOENT}] Directory does not exist: {str(dest_dir)!r}")
    elif not dest_dir.is_dir():
        raise NotADirectoryError(f"[Errno {errno.ENOTDIR}] Not a directory: {str(dest_dir)!r}")

    try:
        tmp_path = f"{path}.part"
        with open(tmp_path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=indent, sort_keys=sort_keys)

        # You could move the atomicity code higher in the function, but then
        # you wouldn't be testing the function for the worst case scenario
        if save_json.__katalytic_test_atomicity_race_condition__:
            save_json.__katalytic_test_atomicity_race_condition__ = False

            # I can't use save_json([{"hello": "world", "race": "condition"}], path) directly
            # It would replace the tmp_path = f'{path}.part' created above
            # and then move it to the target `path`. This function wouldn't
            # be able to find the tmp_path anymore and will throw an error
            # at the end of the function: `Path(tmp_path).rename(path)`
            tmp_path_2 = path.replace(".json", ".2.json")
            save_json([{"hello": "world", "race": "condition"}], tmp_path_2)
            Path(tmp_path_2).rename(path)

        # Checking these conditions again to make the function
        # as robust as possible against race conditions
        if Path(path).exists():
            if exists == "error":
                raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(path)!r}")
            elif exists == "replace":
                pass  # continue executing
            elif exists == "skip":
                return

        if save_json.__katalytic_test_atomicity_interrupt__:
            save_json.__katalytic_test_atomicity_interrupt__ = False
            raise KatalyticInterrupt("Testing atomicity ...")

        Path(tmp_path).rename(path)
    except BaseException as e:
        if not isinstance(e, KatalyticInterrupt):
            raise


@mark("load::txt")
def load_text(path, *, default=_UNDEFINED, encoding="utf-8"):
    """Load data from a text file.

    Args:
        path (str):
            The path to the text file.
        default (Any):
            The default value to return if the specified file path does not exist.
        encoding (str, optional):
            The encoding of the text file. Defaults to 'utf-8'.

    Returns:
        str:
            The text content read from the file.

    Raises:
        FileNotFoundError:
            If the specified file path does not exist.
        IOError:
            If there is an error while reading the text file.
    """
    # Using the wrong extension would return default or raise an error even if the file exists.
    # Trigger the warning before that happens, to provide a hint to the user about the real problem
    _warn_if_another_function_should_be_used(path, _load_funcs)
    if not Path(path).exists() and default is not _UNDEFINED:
        return default

    with open(path, encoding=encoding) as f:
        return f.read()


@mark("save::txt")
def save_text(data, path, *, encoding="utf-8", exists="replace", make_dirs=True):
    """Save data to a text file.

    Args:
        data (str):
            The text content to be saved.
        path (str):
            The path to the output text file.
        encoding (str, optional):
            The encoding of the text file. Defaults to 'utf-8'.
        exists (str, optional):
            Specifies the behavior if the destination file already exists. Defaults to 'replace'.

            - 'error': Raise an error.
            - 'replace': Replace the existing file.
            - 'skip': Skip copying the file.
        make_dirs (bool or str, optional):
            Specifies whether to create the destination directory if it doesn't exist. Defaults to True.

            - True: Create the directory if it doesn't exist.
            - False: Raise an error if the destination directory doesn't exist.

    Returns:
        int:
            The number of characters written to the file.

    Raises:
        IOError:
            If there is an error while saving the text file.
    """
    if exists not in ("error", "replace", "skip"):
        raise ValueError(f'<exists> expects "error", "replace", or "skip". Got {exists!r}')
    elif not isinstance(make_dirs, bool):
        raise TypeError(f"<make_dirs> expects False, or True. Got {make_dirs!r}")

    # optimization: trigger the warning only if the preconditions are valid
    _warn_if_another_function_should_be_used(path, _save_funcs)
    if Path(path).exists():
        if exists == "error":
            raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(path)!r}")
        elif exists == "replace":
            pass  # continue executing
        elif exists == "skip":
            return

    dest_dir = Path(path).parent
    try:
        if make_dirs:
            make_dir(dest_dir, create_parents=True, exists_ok=True)
        elif not dest_dir.exists():
            raise FileNotFoundError(f"[Errno {errno.ENOENT}] Directory does not exist: {str(dest_dir)!r}")
        elif not dest_dir.is_dir():
            raise NotADirectoryError(f"[Errno {errno.ENOTDIR}] Not a directory: {str(dest_dir)!r}")

        tmp_path = f"{path}.part"
        with open(tmp_path, "w", encoding=encoding) as f:
            f.write(data)

        # You could move the atomicity code higher in the function, but then
        # you wouldn't be testing the function for the worst case scenario
        if save_text.__katalytic_test_atomicity_race_condition__:
            save_text.__katalytic_test_atomicity_race_condition__ = False

            # I can't use save_text('race condition', path) directly
            # It would replace the tmp_path = f'{path}.part' created above
            # and then move it to the target `path`. This function wouldn't
            # be able to find the tmp_path anymore and will throw an error
            # at the end of the function: `Path(tmp_path).rename(path)`
            tmp_path_2 = path.replace(".txt", ".2.txt")
            save_text("race condition", tmp_path_2)
            Path(tmp_path_2).rename(path)

        # Checking these conditions again to make the function
        # as robust as possible against race conditions
        if Path(path).exists():
            if exists == "error":
                raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(path)!r}")
            elif exists == "replace":
                pass  # continue executing
            elif exists == "skip":
                return

        if save_text.__katalytic_test_atomicity_interrupt__:
            save_text.__katalytic_test_atomicity_interrupt__ = False
            raise KatalyticInterrupt("Testing atomicity ...")

        Path(tmp_path).rename(path)
    except BaseException as e:
        if not isinstance(e, KatalyticInterrupt):
            raise


def clear_dir(path, *, create_missing=True):
    """Clear the contents of a directory.

    This function is not named "empty_dir" to avoid confusing it with "is_dir_empty".

    Args:
        path (str or Path):
            The path to the directory to be cleared.
        create_missing (bool, optional):
            Specifies whether to create the directory if it does not exist.
            If True, the directory will be created. If False, an error will be raised
            if the directory does not exist. Defaults to True.

    Returns:
        None

    Raises:
        TypeError:
            If <create_missing> is not a boolean value.
        OSError:
            If there is an error while deleting or creating the directory.
    """
    if not isinstance(create_missing, bool):
        raise TypeError(f"<create_missing> expects False or True. Got {type(create_missing)}")

    path = Path(path)
    delete_dir(path, missing_ok=True, non_empty_dir="delete")
    if create_missing:
        make_dir(path)


def copy_dir(src, dest, *, dir_exists="merge", file_exists="replace", make_dirs=True):
    """Copy a directory from source to destination, including its contents.

    Args:
        src (str or Path):
            The path to the source directory.
        dest (str or Path):
            The path to the destination directory.
        dir_exists (str, optional):
            Specifies the behavior if the destination directory already exists. Defaults to 'merge'.

            - 'error': Raise an error.
            - 'merge': Merge the source and destination directories.
            - 'replace': Replace the destination directory with the source directory.
            - 'skip': Skip copying and return.
        file_exists (str, optional):
            Specifies the behavior if a file with the same name already exists
            in the destination directory. Defaults to 'replace'.

            - 'error': Raise an error.
            - 'replace': Replace the existing file.
            - 'skip': Skip copying the file.
        make_dirs (bool, optional):
            Specifies whether to create the destination directory if it doesn't exist. Defaults to True.

            - True: Create the directory if it doesn't exist.
            - False: Raise an error if the destination directory doesn't exist.

    Returns:
        None

    Raises:
        ValueError:
            If invalid values are provided for the 'dir_exists' or 'file_exists' parameters.
        TypeError:
            If the 'make_dirs' parameter is not a boolean value.
        FileNotFoundError:
            If the source directory doesn't exist or the destination directory cannot be created.
        NotADirectoryError:
            If the source or destination path is not a directory.
        FileExistsError:
            If a destination directory already exists when 'dir_exists' is set to 'error'.
        OSError:
            If there is an error while copying or deleting files/directories.
    """
    if dir_exists not in ("error", "merge", "replace", "skip"):
        raise ValueError(f'<dir_exists> expects "error", "merge", "replace", "skip". Got {dir_exists!r}')
    elif file_exists not in ("error", "replace", "skip"):
        raise ValueError(f'<file_exists> expects "error", False, or True. Got {file_exists!r}')
    elif not isinstance(make_dirs, bool):
        raise TypeError(f"<make_dirs> expects False or True. Got {type(make_dirs)}")

    src = Path(src)
    dest = Path(dest)

    if not src.exists():
        raise FileNotFoundError(f"[Errno {errno.ENOENT}] <src> directory does not exist: {str(src)!r}")
    elif src.is_file():
        raise NotADirectoryError(f"[Errno {errno.ENOTDIR}] Expected a directory, but <src> is a file: {str(src)!r}")
    elif dest.is_file():
        raise NotADirectoryError(f"[Errno {errno.ENOTDIR}] Expected a directory, but <dest> is a file: {str(dest)!r}")
    elif dest.is_dir():
        if dir_exists == "error":
            raise FileExistsError(f"[Errno {errno.EEXIST}] Directory already exists: {str(dest)!r}")
        elif src.samefile(dest):
            raise ValueError(f"<src> and <dest> are equal: {str(src)!r}")
        elif dir_exists == "replace":
            delete_dir(dest, non_empty_dir="delete")
        elif dir_exists == "skip":
            return
    elif not make_dirs:
        raise FileNotFoundError(f"[Errno {errno.ENOENT}] No such directory: {str(dest)!r}")

    try:
        # You could move the atomicity code higher in the function, but then
        # you wouldn't be testing the function for the worst case scenario
        if copy_dir.__katalytic_test_atomicity_race_condition__:
            copy_dir.__katalytic_test_atomicity_race_condition__ = False

            # I can't use copy_dir([{'race': 'condition'}], path) directly
            # It would replace the tmp_path = f'{path}.part' created above
            # and then move it to the target `path`. This function wouldn't
            # be able to find the tmp_path anymore and will throw an error
            # at the end of the function: `Path(tmp_path).rename(path)`
            make_dir(dest)

        # Checking these conditions again to make the function
        # as robust as possible against race conditions
        if Path(dest).is_dir():
            if dir_exists == "error":
                raise FileExistsError(f"[Errno {errno.EEXIST}] Directory exists: {str(dest)!r}")
            elif dir_exists == "replace":
                pass  # continue executing
            elif dir_exists == "skip":
                return

        if copy_dir.__katalytic_test_atomicity_interrupt__:
            copy_dir.__katalytic_test_atomicity_interrupt__ = False
            raise KatalyticInterrupt()

        if make_dirs:
            if src.name != dest.name:
                dest = dest / src.name

            make_dir(dest)

        for src_item in src.iterdir():
            dest_item = str(src_item).replace(str(src), str(dest))
            if src_item.is_dir():
                copy_dir(src_item, dest_item, make_dirs=make_dirs, file_exists=file_exists, dir_exists=dir_exists)
            else:
                copy_file(src_item, dest_item, exists=file_exists)
    except BaseException as e:
        if not isinstance(e, KatalyticInterrupt):
            raise


def copy_file(src, dest, *, exists="replace", make_dirs=True):
    """Copy a file from source to destination.

    Args:
        src (str or Path):
            The path to the source file.
        dest (str or Path):
            The path to the destination file.
        exists (str, optional):
            Specifies the behavior if the destination file already exists. Defaults to 'replace'.

            - 'error': Raise an error.
            - 'replace': Replace the existing file.
            - 'skip': Skip copying the file.
        make_dirs (bool or str, optional):
            Specifies whether to create the destination directory if it doesn't exist. Defaults to True.

            - True: Create the directory if it doesn't exist.
            - False: Raise an error if the destination directory doesn't exist.

    Returns:
        None

    Raises:
        ValueError:
            If invalid values are provided for the 'exists' or 'make_dirs' parameters.
        FileNotFoundError:
            If the source file doesn't exist or the destination directory cannot be created.
        ValueError:
            If the source and destination paths are the same.
        IsADirectoryError:
            If the source path is a directory.
        FileExistsError:
            If a destination file already exists when 'exists' is set to 'error'.
        OSError:
            If there is an error while copying or deleting the file.
    """
    if exists not in ("error", "replace", "skip"):
        raise ValueError(f'<exists> expects "error", "replace", or "skip". Got {exists!r}')
    elif not isinstance(make_dirs, bool):
        raise TypeError(f"<make_dirs> expects False or True. Got {type(make_dirs)}")

    src = Path(src)
    dest = Path(dest)

    if src.exists() and dest.exists() and src.samefile(dest):
        raise ValueError(f"<src> and <dest> are equal: {str(src)!r}")
    elif not src.exists():
        raise FileNotFoundError(f"[Errno {errno.ENOENT}] <src> file does not exist: {str(src)!r}")
    elif src.is_dir():
        raise IsADirectoryError(f"[Errno {errno.EISDIR}] Expected a file, but <src> is a directory: {str(src)!r}")

    try:
        if dest.exists():
            if exists == "error":
                raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(dest)!r}")
            elif exists == "replace":
                pass
            elif exists == "skip":
                return
        elif make_dirs:
            make_dir(dest.parent)
        else:
            raise FileNotFoundError(f"[Errno {errno.ENOENT}] No such file: {str(dest)!r}")

        # You could move the atomicity code higher in the function, but then
        # you wouldn't be testing the function for the worst case scenario
        if copy_file.__katalytic_test_atomicity_race_condition__:
            copy_file.__katalytic_test_atomicity_race_condition__ = False

            # I can't use copy_file([{'race': 'condition'}], path) directly
            # It would replace the tmp_path = f'{path}.part' created above
            # and then move it to the target `path`. This function wouldn't
            # be able to find the tmp_path anymore and will throw an error
            # at the end of the function: `Path(tmp_path).rename(path)`
            Path(dest).write_text("race condition")

        # Checking these conditions again to make the function
        # as robust as possible against race conditions
        if Path(dest).exists():
            if exists == "error":
                raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(dest)!r}")
            elif exists == "replace":
                pass  # continue executing
            elif exists == "skip":
                return

        if copy_file.__katalytic_test_atomicity_interrupt__:
            copy_file.__katalytic_test_atomicity_interrupt__ = False
            raise KatalyticInterrupt()

        shutil.copy2(src, dest)
    except BaseException as e:
        if not isinstance(e, KatalyticInterrupt):
            raise


def delete_dir(path, *, missing_ok=True, non_empty_dir="delete"):
    """Delete a directory.

    Args:
        path (str or Path):
            The path to the directory to be deleted.
        missing_ok (bool, optional):
            Specifies whether it is okay if the directory doesn't exist. Defaults to True.

            - True: No error is raised if the directory doesn't exist.
            - False: Raise an error if the directory doesn't exist.
        non_empty_dir (str or bool, optional):
            Specifies the behavior if the directory is non-empty.  Defaults to True.

            - 'error': Raise an error if the directory is non-empty.
            - 'delete': Delete the directory and its contents, recursively.
            - 'skip': Don't delete the directory.

    Returns:
        None

    Raises:
        ValueError:
            If the provided path is empty or refers to the current directory.
            If invalid values are provided for the 'missing_ok' or 'non_empty_dir' parameters.
        TypeError:
            If the 'missing_ok' parameter is not a boolean value.
        FileNotFoundError:
            If the directory doesn't exist and 'missing_ok' is set to False.
        NotADirectoryError:
            If the provided path refers to a file instead of a directory.
        RuntimeError:
            If there is an error while deleting the directory.
    """
    if path is None or path in ("", "."):
        raise ValueError(f"path={path!r} would delete the current dir")
    elif not isinstance(missing_ok, bool):
        raise TypeError(f"<missing_ok> expects False or True. Got {type(missing_ok)}")
    elif is_none_of(non_empty_dir, ("delete", "error", "skip")):
        raise ValueError(f'<non_empty_dir> expects "error", False, or True. Got {non_empty_dir!r}')

    path = Path(path)
    if path.is_dir():
        if not is_dir_empty(path):
            if non_empty_dir == "error":
                raise RuntimeError(f"The {str(path)!r} directory is not empty")
            elif non_empty_dir == "delete":
                shutil.rmtree(path)
        else:
            path.rmdir()
    elif not path.exists():
        if missing_ok:
            pass
        else:
            raise FileNotFoundError(f"[Errno {errno.ENOENT}] No such directory: {str(path)!r}")
    elif path.is_file():
        raise NotADirectoryError(f"[Errno {errno.ENOTDIR}] Expected a directory, but <path> is a file: {str(path)!r}")


def delete_file(path, *, missing_ok=True):
    """Delete a file.

    Args:
        path (str or Path):
            The path to the file to be deleted.
        missing_ok (bool, optional):
            Specifies whether it is okay if the file doesn't exist. Defaults to True.

            - True: No error is raised if the file doesn't exist.
            - False: Raise an error if the file doesn't exist.

    Returns:
        None

    Raises:
        TypeError:
            If the 'missing_ok' parameter is not a boolean value.
        FileNotFoundError:
            If the file doesn't exist and 'missing_ok' is set to False.
        IsADirectoryError:
            If the provided path refers to a directory instead of a file.
        OSError:
            If there is an error while deleting the file.
    """
    if not isinstance(missing_ok, bool):
        raise TypeError(f"<missing_ok> expects False or True. Got {type(missing_ok)}")

    path = Path(path)
    if path.is_file():
        path.unlink()
    elif not path.exists():
        if missing_ok:
            pass
        else:
            raise FileNotFoundError(f"[Errno {errno.ENOENT}] No such file: {str(path)!r}")
    elif path.is_dir():
        raise IsADirectoryError(f"[Errno {errno.EISDIR}] Expected a file, but <path> is a directory: {str(path)!r}")


def get_all(path=".", *, glob=True, iter_=False, prefix=True, recursive=False):
    """Retrieve all files and directories at the specified path. If `iter_` is False,
    they will be sorted.

    Args:
        path (str or Path, optional):
            The path to retrieve files and directories from. Defaults to the current directory ('.').
        glob (bool, optional):
            Specifies whether to use glob pattern matching to retrieve files and directories. Defaults to True.
        iter_ (bool, optional):
            Specifies whether to return an iterator instead of a list of results. Defaults to False.
        prefix (bool, optional):
            Specifies whether to include the path prefix in the returned results. Defaults to True.
        recursive (bool, optional):
            Specifies whether to retrieve files and directories recursively. Defaults to False.

    Returns:
        list or iterator:
            A list of files and directories at the specified path, or an iterator if `iter_` is set to True.
    """
    return _get_all(path, glob=glob, iter_=iter_, prefix=prefix, recursive=recursive)


def get_dirs(path=".", *, glob=True, iter_=False, prefix=True, recursive=False):
    """Retrieve directories at the specified path. If `iter_` is False, they will be
    sorted.

    Args:
        path (str or Path, optional):
            The path to retrieve directories from. Defaults to the current directory ('.').
        glob (bool, optional):
            Specifies whether to use glob pattern matching to retrieve directories. Defaults to True.
        iter_ (bool, optional):
            Specifies whether to return an iterator instead of a list of results. Defaults to False.
        prefix (bool, optional):
            Specifies whether to include the path prefix in the returned results. Defaults to True.
        recursive (bool, optional):
            Specifies whether to retrieve directories recursively. Defaults to False.

    Returns:
        list or iterator:
            A list of directories at the specified path, or an iterator if `iter_` is set to True.
    """
    return _get_all(path, glob=glob, iter_=iter_, prefix=prefix, only_dirs=True, recursive=recursive)


def get_files(path=".", *, glob=True, iter_=False, prefix=True, recursive=False):
    """Retrieve files at the specified path. If `iter_` is False, they will be sorted.

    Args:
        path (str or Path, optional):
            The path to retrieve files from. Defaults to the current directory ('.').
        glob (bool, optional):
            Specifies whether to use glob pattern matching to retrieve files. Defaults to True.
        iter_ (bool, optional):
            Specifies whether to return an iterator instead of a list of results. Defaults to False.
        prefix (bool, optional):
            Specifies whether to include the path prefix in the returned results. Defaults to True.
        recursive (bool, optional):
            Specifies whether to retrieve files recursively. Defaults to False.

    Returns:
        list or iterator:
            A list of files at the specified path, or an iterator if `iter_` is set to True.
    """
    return _get_all(path, glob=glob, iter_=iter_, prefix=prefix, only_files=True, recursive=recursive)


def _get_all(path=".", *, glob=True, iter_=False, only_dirs=False, only_files=False, prefix=True, recursive=False):
    """Retrieve all files and directories at the specified path. If `iter_` is False,
    they will be sorted.

    Args:
        path (str or Path, optional):
            The path to retrieve files and directories from. Defaults to the current directory ('.').
        glob (bool, optional):
            Specifies whether to use glob pattern matching to retrieve files and directories. Defaults to True.
        iter_ (bool, optional):
            Specifies whether to return an iterator instead of a list of results. Defaults to False.
        only_dirs (bool, optional):
            Specifies whether to retrieve only directories. Defaults to False.
        only_files (bool, optional):
            Specifies whether to retrieve only files. Defaults to False.
        prefix (bool, optional):
            Specifies whether to include the path prefix in the returned results. Defaults to True.
        recursive (bool, optional):
            Specifies whether to retrieve files and directories recursively. Defaults to False.

    Returns:
        list or iterator:
            A list of files and directories at the specified path, or an iterator if `iter_` is set to True.

    Raises:
        TypeError:
            If invalid values are provided for the boolean parameters.
        ValueError:
            If both 'only_dirs' and 'only_files' are set to True.
    """
    if not is_pathlike(path):
        raise TypeError(f"<path> expects a string or a Path object. Got {type(path)}")
    elif not isinstance(glob, bool):
        raise TypeError(f"<glob> expects False or True. Got {type(glob)}")
    elif not isinstance(iter_, bool):
        raise TypeError(f"<iter_> expects False or True. Got {type(iter_)}")
    elif not isinstance(only_dirs, bool):
        raise TypeError(f"<only_dirs> expects False or True. Got {type(only_dirs)}")
    elif not isinstance(only_files, bool):
        raise TypeError(f"<only_files> expects False or True. Got {type(only_files)}")
    elif not isinstance(prefix, bool):
        raise TypeError(f"<prefix> expects False or True. Got {type(prefix)}")
    elif not isinstance(recursive, bool):
        raise TypeError(f"<recursive> expects False or True. Got {type(recursive)}")
    elif only_dirs and only_files:
        raise ValueError("<only_dirs> and <only_files> can't be True at the same time")

    original_type = type(path)
    if glob and "*" in str(path):
        path, _, pattern = str(path).partition("*")
        if recursive:
            pattern = re.sub(r"^\*/", r"**/", f"*{pattern}")
            result = Path(path).rglob(pattern)
        else:
            result = Path(path).glob(f"*{pattern}")
    else:
        result = Path(path).iterdir()
        if recursive:
            result = itertools.chain.from_iterable(
                (
                    [p]
                    if p.is_file()
                    else itertools.chain(
                        [p],
                        _get_all(
                            p,
                            glob=glob,
                            iter_=True,
                            only_dirs=only_dirs,
                            only_files=only_files,
                            prefix=True,
                            recursive=recursive,
                        ),
                    )
                )
                for p in result
            )

    if only_dirs:
        result = (p for p in result if Path(p).is_dir())
    elif only_files:
        result = (p for p in result if Path(p).is_file())

    if prefix:
        result = (str(p) for p in result)
    else:
        result = (str(p).replace(f"{path}/", "", 1) for p in result)

    result = (original_type(p) for p in result)

    if iter_:
        return result
    else:
        return sorted(result)


def get_unique_path(pattern="{}"):
    """Generate a unique path based on the provided pattern.

    Args:
        pattern (str or Path, optional):
            The pattern for generating the unique path. Defaults to '{}'.

    Returns:
        str:
            A unique path generated based on the pattern.

    Raises:
        TypeError:
            If the 'pattern' parameter is not a string or a pathlib.Path object.
        ValueError:
            If the pattern is invalid or does not contain exactly one placeholder.
    """
    if not isinstance(pattern, (str, Path)):
        raise TypeError(f"<pattern> expects a str or pathlib.Path. Got {type(pattern)}")

    original_type = type(pattern)
    pattern = str(pattern)
    placeholders = re.findall(r"{(:((\d*)?d)?)?}", pattern)
    if len(placeholders) != 1:
        raise ValueError(
            f"Invalid pattern: {pattern!r}. You must provide exactly one placeholder, "
            + 'optionally with an integer format. Try using "{}" or "{:03d}"'
        )

    if pattern.startswith("./"):
        pattern = pattern.partition("./")[2]

    if not pattern.startswith("/"):
        d = tempfile.mkdtemp()
        pattern = f"{d}/{pattern}"

    n = 0
    while True:
        n += 1
        path = pattern.format(n)
        if not Path(path).exists():
            return original_type(path)


def is_dir_empty(path, *, missing="error"):
    """Check if a directory is empty.

    Args:
        path (str or Path):
            The path to the directory.
        missing (bool or str, optional):
            Specifies the behavior if the directory doesn't exist. Defaults to 'error'.

            - True: Return True if the directory doesn't exist.
            - False: Return False if the directory doesn't exist.
            - 'error': Raise an error if the directory doesn't exist.

    Returns:
        bool:
            True if the directory is empty, False otherwise.

    Raises:
        ValueError:
            If invalid values are provided for the 'missing' parameter.
        NotADirectoryError:
            If the provided path refers to a file instead of a directory.
        FileNotFoundError:
            If the directory doesn't exist and 'missing' is set to 'error'.
    """
    if is_none_of(missing, (False, True, "error")):
        raise ValueError(f'<missing> expects "error", False, or True. Got {missing!r}')

    path = Path(path)
    if path.is_dir():
        return list(path.iterdir()) == []
    elif path.is_file():
        raise NotADirectoryError(f'[Errno {errno.ENOTDIR}] Expected a directory, but "path" is a file: {str(path)!r}')
    else:
        if missing is False:
            return False
        elif missing is True:
            return True
        elif missing == "error":
            raise FileNotFoundError(f"[Errno {errno.ENOENT}] No such file or directory: {str(path)!r}")


def is_file_empty(path, *, missing="error"):
    """Check if a file is empty.

    Args:
        path (str or Path):
            The path to the file.
        missing (bool or str, optional):
            Specifies the behavior if the file doesn't exist. Defaults to 'error'.

            - True: Return True if the file doesn't exist.
            - False: Return False if the file doesn't exist.
            - 'error': Raise an error if the file doesn't exist.

    Returns:
        bool:
            True if the file is empty, False otherwise.

    Raises:
        ValueError:
            If invalid values are provided for the 'missing' parameter.
        IsADirectoryError:
            If the provided path refers to a directory instead of a file.
        FileNotFoundError:
            If the file doesn't exist and 'missing' is set to 'error'.
    """
    if is_none_of(missing, (False, True, "error")):
        raise ValueError(f'<missing> expects "error", False, or True. Got {missing!r}')

    path = Path(path)
    if path.is_file():
        return path.stat().st_size == 0
    elif path.is_dir():
        raise IsADirectoryError(f"[Errno {errno.EISDIR}] Expected a file, but <path> is a directory: {str(path)!r}")
    else:
        if missing is False:
            return False
        elif missing is True:
            return True
        elif missing == "error":
            raise FileNotFoundError(f"[Errno {errno.ENOENT}] No such file or directory: {str(path)!r}")


def make_dir(path, *, create_parents=True, exists_ok=True):
    """Create a directory at the specified path.

    Args:
        path (str or Path):
            The path to the directory.
        create_parents (bool, optional):
            Specifies whether to create parent directories if they don't exist. If set to False
            and the parent directories don't exist, an error will be raised. Defaults to True.
        exists_ok (bool, optional):
            Specifies whether to raise an error if the directory already exists. Defaults to True.

    Returns:
        None

    Raises:
        TypeError:
            If the 'create_parents' or 'exists_ok' parameters are not boolean values.
        NotADirectoryError:
            If the provided path refers to a file instead of a directory.
        FileExistsError:
            If the directory already exists and 'exists_ok' is set to False.
        OSError:
            If there is an error while creating the directory.
    """
    if not isinstance(create_parents, bool):
        raise TypeError(f"<create_parents> expects False or True. Got {type(create_parents)}")
    elif not isinstance(exists_ok, bool):
        raise TypeError(f"<exists_ok> expects False or True. Got {type(exists_ok)}")

    path = Path(path)
    if path.is_file():
        raise NotADirectoryError(f'[Errno {errno.ENOTDIR}] Expected a directory, but "path" is a file: {str(path)!r}')

    path.mkdir(parents=create_parents, exist_ok=exists_ok)


def move_dir(src, dest, *, dir_exists="merge", file_exists="replace", make_dirs=True):
    """Move a directory from source to destination.

    Args:
        src (str or Path):
            The path to the source directory.
        dest (str or Path):
            The path to the destination directory.
        dir_exists (str or bool, optional):
            Specifies the behavior if the destination directory already exists. Defaults to 'merge'.

            - 'error': Raise an error.
            - 'merge': Merge the source and destination directories.
            - 'replace': Replace the destination directory with the source directory.
            - 'skip': Skip copying and return.
        file_exists (str, optional):
            Specifies the behavior if a file with the same name already exists
            in the destination directory. Defaults to 'replace'.

            - 'error': Raise an error.
            - 'replace': Replace the existing file.
            - 'skip': Skip copying the file.
        make_dirs (bool, optional):
            Specifies whether to create the destination directory if it doesn't exist. Defaults to True.

            - True: Create the directory if it doesn't exist.
            - False: Raise an error if the destination directory doesn't exist.

    Returns:
        None
    """
    if dir_exists == "skip" and Path(dest).exists():
        return

    copy_dir(src, dest, dir_exists=dir_exists, file_exists=file_exists, make_dirs=make_dirs)
    delete_dir(src, non_empty_dir="delete")


def move_file(src, dest, *, exists="replace", make_dirs=True):
    """Move a file from source to destination.

    Args:
        src (str or Path):
            The path to the source file.
        dest (str or Path):
            The path to the destination file.
        exists (str, optional):
            Specifies the behavior if the destination file already exists. Defaults to 'replace'.

            - 'error': Raise an error.
            - 'replace': Replace the existing file.
            - 'skip': Skip copying the file.
        make_dirs (bool or str, optional):
            Specifies whether to create the destination directory if it doesn't exist. Defaults to True.

            - True: Create the directory if it doesn't exist.
            - False: Raise an error if the destination directory doesn't exist.

    Returns:
        None
    """
    if exists not in ("error", "replace", "skip"):
        raise ValueError(f'<exists> expects "error", "replace", or "skip". Got {exists!r}')
    elif not isinstance(make_dirs, bool):
        raise TypeError(f"<make_dirs> expects False or True. Got {type(make_dirs)}")

    src = Path(src)
    dest = Path(dest)

    if not src.exists():
        raise FileNotFoundError(f"[Errno {errno.ENOENT}] <src> file does not exist: {str(src)!r}")
    elif src.is_dir():
        raise IsADirectoryError(f"[Errno {errno.EISDIR}] Expected a file, but <src> is a directory: {str(src)!r}")

    try:
        if dest.exists():
            if src.samefile(dest):
                raise ValueError(f"<src> and <dest> are equal: {str(src)!r}")
            elif exists == "error":
                raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(dest)!r}")
            elif exists == "replace":
                pass
            elif exists == "skip":
                return
        elif make_dirs:
            make_dir(dest.parent)
        else:
            raise FileNotFoundError(f"[Errno {errno.ENOENT}] No such file: {str(dest)!r}")

        # You could move the atomicity code higher in the function, but then
        # you wouldn't be testing the function for the worst case scenario
        if move_file.__katalytic_test_atomicity_race_condition__:
            move_file.__katalytic_test_atomicity_race_condition__ = False

            # I can't use move_file([{'race': 'condition'}], path) directly
            # It would replace the tmp_path = f'{path}.part' created above
            # and then move it to the target `path`. This function wouldn't
            # be able to find the tmp_path anymore and will throw an error
            # at the end of the function: `Path(tmp_path).rename(path)`
            Path(dest).write_text("race condition")

        # Checking these conditions again to make the function
        # as robust as possible against race conditions
        if Path(dest).exists():
            if exists == "error":
                raise FileExistsError(f"[Errno {errno.EEXIST}] File exists: {str(dest)!r}")
            elif exists == "replace":
                pass  # continue executing
            elif exists == "skip":
                return

        if move_file.__katalytic_test_atomicity_interrupt__:
            move_file.__katalytic_test_atomicity_interrupt__ = False
            raise KatalyticInterrupt()

        shutil.move(str(src), str(dest))
    except BaseException as e:
        if not isinstance(e, KatalyticInterrupt):
            raise


def _find_grouped_functions(group):
    function_dispatcher = {}
    for func_name, f, groups in find_functions_marked_with(group):
        for g in groups:
            ext = g.rpartition("::")[2]
            function_dispatcher[ext] = f

    # sort the dict with the most specific extension at the beginning
    # this makes it easier to pick ".tar.gz" over ".gz"
    return sort_dict_by_keys(function_dispatcher, condition=len, reverse=True)


_load_funcs = _find_grouped_functions("load::*")
_save_funcs = _find_grouped_functions("save::*")


def load(path, default=_UNDEFINED, **kwargs):
    """Load data from a file based on the file extension.

    Args:
        path (str):
            The path to the input file.
        default (Any):
            The default value to return if the specified file path does not exist.
        **kwargs:
            Additional keyword arguments to be passed to the specific load function.

    Returns:
        any:
            The loaded data from the file.

    Raises:
        RuntimeError:
            If no load function is found for the given file extension.
    """
    for ext, f in _load_funcs.items():
        if path.lower().endswith(f".{ext}"):
            return f(path, default=default, **kwargs)

    return load_text(path, default=default, **kwargs)


def save(data, path, *, exists="replace", make_dirs=True, **kwargs):
    """Save data to a file based on the file extension.

    Args:
        data (any):
            The data to be saved.
        path (str):
            The path to the output file.
        exists (str, optional):
            Specifies the behavior if the destination file already exists. Defaults to 'replace'.

            - 'error': Raise an error.
            - 'replace': Replace the existing file.
            - 'skip': Skip copying the file.
        make_dirs (bool or str, optional):
            Specifies whether to create the destination directory if it doesn't exist. Defaults to True.

            - True: Create the directory if it doesn't exist.
            - False: Raise an error if the destination directory doesn't exist.
        **kwargs:
            Additional keyword arguments to be passed to the specific save function.

    Returns:
        None

    Raises:
        RuntimeError:
            If no save function is found for the given file extension.
    """
    for ext, f in _save_funcs.items():
        if path.lower().endswith(f".{ext}"):
            f(data, path, exists=exists, make_dirs=make_dirs, **kwargs)
            return

    save_text(data, path, exists=exists, make_dirs=make_dirs, **kwargs)


def _warn_if_another_function_should_be_used(path, group_dict):
    path = path.lower()
    for ext, f in group_dict.items():
        if path.endswith(f".{ext}"):
            file, caller, line = extract_call_stack_info(depth=1)
            if group_dict[ext] != caller:
                warnings.warn(
                    f'Use "{group_dict[ext].__name__}" for ".{ext}" files instead of "{caller.__name__}".'
                    f"\n(called from {file}:{line})"
                )
            break


copy_dir.__katalytic_test_atomicity_interrupt__ = False
copy_file.__katalytic_test_atomicity_interrupt__ = False
move_dir.__katalytic_test_atomicity_interrupt__ = False
move_file.__katalytic_test_atomicity_interrupt__ = False
save_csv.__katalytic_test_atomicity_interrupt__ = False
save_json.__katalytic_test_atomicity_interrupt__ = False
save_text.__katalytic_test_atomicity_interrupt__ = False

copy_dir.__katalytic_test_atomicity_race_condition__ = False
copy_file.__katalytic_test_atomicity_race_condition__ = False
move_dir.__katalytic_test_atomicity_race_condition__ = False
move_file.__katalytic_test_atomicity_race_condition__ = False
save_csv.__katalytic_test_atomicity_race_condition__ = False
save_json.__katalytic_test_atomicity_race_condition__ = False
save_text.__katalytic_test_atomicity_race_condition__ = False
