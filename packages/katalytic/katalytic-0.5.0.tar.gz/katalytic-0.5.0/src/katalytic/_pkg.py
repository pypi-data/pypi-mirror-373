import pkgutil
import re
import sys
import traceback
import warnings
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
from glob import iglob
from importlib import import_module
from pathlib import Path

_pkg_whitelist = ("katalytic", "katalytic_images")


def _is_katalytic_test(module_str: str) -> bool:
    if module_str != "tests.test_pkg":
        return False

    return import_module(module_str).__file__.endswith("/katalytic/tests/test_pkg.py")


def _function():
    pass


def _generator():
    yield 1


class _C:
    def __call__(self, *args, **kwargs):
        pass


_map = map(int, [])
_C_obj = _C()
_obj = object()
_lambda = lambda x: x
_generator_expr = (x for x in [])
_sequences = [[], (), range(0)]
_dict_views = [{}.keys(), {}.values(), {}.items()]
_iterators = [_generator, _generator_expr, iter([]), _map, enumerate([]), zip([], [], strict=False)]
_iterables = [*_dict_views, *_iterators, *_sequences, set(), {}]
_collections = [(), set(), frozenset([]), {}, []]
_booleans = [True, False]
_singletons = [None, True, False]
_primitives = [*_singletons, 0, 0.0, "", b"", bytearray(b"")]
_callables = [_generator, _function, _lambda, _C_obj, _C]
_numbers = [0, 0.0, 0j, Decimal("0"), Fraction(0, 1)]
_objects = [_obj, _C_obj]
_generators = [_generator, _generator_expr]
_functions = [_generator, _function, _lambda]
_strings = ["", b"", bytearray(b"")]
_types = {
    "booleans": _booleans,
    "bytearray": bytearray(b""),
    "bytes": b"",
    "callables": _callables,
    "callable_obj": _C_obj,
    "class": _C,
    "collections": _collections,
    "complex": 0 + 0j,
    "decimal": Decimal("0"),
    "dict": {},
    "dict_views": _dict_views,
    "float": 0.0,
    "fraction": Fraction(0, 1),
    "frozenset": frozenset([]),
    "functions": _functions,
    "generator_expression": _generator_expr,
    "generator_function": _generator,
    "generators": _generators,
    "int": 0,
    "iterables": _iterables,
    "iterators": _iterators,
    "list": [],
    "map": _map,
    "none": None,
    "numbers": _numbers,
    "objects": _objects,
    "path": Path(""),
    "pathlike": ["", Path("")],
    "primitives": _primitives,
    "sequences": _sequences,
    "set": set(),
    "singletons": _singletons,
    "str": "",
    "strings": _strings,
    "tuple": (),
}


def all_types(whitelist=None):
    """Get all supported types or a subset of types based on a whitelist.

    Args:
        whitelist (str or Iterable[str], optional):
            A whitelist of type names to include. If None, all supported types are returned.
            If a string, it is treated as a single type name.
            If an iterable of strings, it is treated as a collection of type names.
            Defaults to None.

    Returns:
        list: A list of values for each type in the whitelist.

    Raises:
        TypeError: If whitelist is not None, a str, or an iterable.
        ValueError: If unexpected type names are present in the whitelist.

    Examples:
        >>> all_types('numbers')
        [0, 0.0, 0j, Decimal('0'), Fraction(0, 1)]
        >>> all_types('singletons')
        [None, True, False]
    """
    from katalytic.data.checks import is_iterable

    if whitelist is None:
        return _flatten(_types.values())
    elif isinstance(whitelist, str):
        whitelist = [whitelist]
    elif not is_iterable(whitelist):
        raise TypeError(f"<whitelist> must be iterable. Got {type(whitelist).__name__}")

    unexpected = set(whitelist) - set(_types.keys())
    if unexpected:
        raise ValueError(f"Unexpected types in <whitelist>: {unexpected}")

    return _flatten(_types[t] for t in whitelist)


def all_types_besides(blacklist):
    """Get all supported types except those specified in the blacklist.

    Args:
        blacklist (str or Iterable[str]):
            A list of type names to exclude. If a string, it is treated as a single type name.
            If an iterable of strings, it is treated as a collection of type names.

    Returns:
        list: A list of values for each type not in the blacklist.

    Raises:
        TypeError: If blacklist is not a str or iterable.
        ValueError: If unexpected type names are present in the blacklist.

    Examples:
        >>> all_types_besides(['iterables', 'generators', 'functions', 'objects', 'path', 'numbers', 'class'])
        [True, bytearray(b''), b'', None, '']
    """
    from katalytic.data.checks import is_iterable

    if isinstance(blacklist, str):
        blacklist = [blacklist]
    elif not is_iterable(blacklist):
        raise TypeError(f"<blacklist> must be iterable. Got {type(blacklist).__name__}")

    blacklist = set(blacklist)
    unexpected = blacklist - set(_types.keys())
    if unexpected:
        raise ValueError(f"Unexpected types in <blacklist>: {unexpected}")

    to_remove = _flatten(_types[t] for t in blacklist)
    all_types = _flatten(_types.values())
    kept = []
    for t in all_types:
        if t in to_remove:
            continue

        # remove duplicates too
        # I have to do it this way because python considers
        # 0 == 0.0 == 0j == Decimal('0') == Fraction(0, 1)
        if (t, type(t)) in [(x, type(x)) for x in kept]:
            continue

        kept.append(t)

    return kept


def _flatten(iterable):
    """Flatten iterable with some special rules to make all_types() and
    all_types_besides() work correctly. Use flatten() for everything else.

    Args:
        iterable (Iterable): The iterable to flatten.

    Returns:
        list: An iterable flattened by one level.

    Raises:
        TypeError: If the input is not an iterable.
    """
    from katalytic.data.checks import is_iterable

    if not is_iterable(iterable):
        raise TypeError(f"<iterable> expects an iterable. Got {type(iterable).__name__}")

    flat = []
    for x in iterable:
        if isinstance(x, (dict, set, list, tuple)) and len(x):
            flat.extend(x)
        else:
            flat.append(x)

    return flat


def __get_version_from_metadata(path):
    with open(path) as f:
        for line in f:
            if line.startswith("Version:"):
                return line.split(":")[-1].strip()


def __find_paths(pkg):
    pkg = pkg.replace("-", "_").replace(".", "_")
    for p in sys.path:
        if not Path(p).is_dir():
            continue

        for p2 in iglob(f"{p}/**.dist-info", recursive=True):
            if re.search(f"{pkg}-[^/]*[.]dist-info", p2):
                yield p2
                if Path(f"{p2}/METADATA").is_file():
                    yield p2

        for p2 in iglob(f"{p}/**.egg-info", recursive=True):
            if re.search(f"{pkg}-[^/]*[.]egg-info", p2):
                yield p2
                if Path(f"{p2}/PKG-INFO").is_file():
                    yield f"{p2}/PKG-INFO"


class KatalyticInterrupt(Exception):
    """This exception is used in testing how code behaves when it gets interrupted.

    I can catch all exceptions and re-raise if it's not this one
    """


def get_version(dunder_name):  # pragma: no cover -- I can't test all branches at the same time
    """Get the version information for a package.

    Args:
        dunder_name (str):
            The dunder name of the package (i.e., __name__).

    Returns:
        tuple:
            A tuple containing the version string and the version information as a tuple of integers.
            If the version information cannot be determined, None is returned.
    """
    if sys.version_info >= (3, 8):
        from importlib import metadata

        dunder_name = dunder_name.replace(".", "-")
        dunder_name = dunder_name.replace("-__init__", "")
        version = metadata.version(dunder_name)

        version_info = version.replace("+editable", "").split(".")
        version_info = tuple(map(int, version_info))
        if "+editable" in version:
            version_info = (*version_info, "editable")

        return version, version_info

    version = None
    for p in __find_paths(dunder_name):
        if p.endswith(".dist-info"):
            version = re.search(r"\w+-(\d+\.\d+\.\d+)", p)
            if version:
                version = version.group(1)
                break

        if p.endswith(".dist-info/METADATA") or p.endswith(".egg-info/PKG-INFO"):
            version = __get_version_from_metadata(p)
            if version:
                break

    if version:
        version_info = version.replace("+editable", "").split(".")
        version_info = tuple(map(int, version_info))
        if "+editable" in version:
            version_info = (*version_info, "editable")
    else:
        version_info = None

    # If nothing worked, I would rather return None than raise an exception
    # This could happen if the package is installed on python < 3.8
    return version, version_info


def _get_stacktrace(e):
    return "".join(traceback.format_exception(None, e, e.__traceback__))


def _check(name, group):
    if group.endswith("*"):
        prefix = group.split("*")[0]
        return name.startswith(prefix)
    else:
        return name == group


@lru_cache(maxsize=1)
def get_katalytic_modules():
    """Get a list of importable modules within the package.

    Returns:
        list:
            A list of importable modules within the package, sorted by module name.
    """

    modules = []
    for p in _pkg_whitelist:
        try:
            p = import_module(p)
        except ModuleNotFoundError:
            continue  # Don't force users to install all the plugins

        modules.extend(_get_modules_recursive(p.__path__))

    return sorted(modules, key=lambda m: m.__name__)


def _get_modules_recursive(pkg_path, parent=None):
    modules = []
    for m in pkgutil.walk_packages(pkg_path):
        package_name = m.module_finder.path.split("/")[-1]
        if parent:
            package_name = f"{parent}.{package_name}"

        module_path = f"{package_name}.{m.name}"
        if module_path == "data.data.x":
            continue  # I don't know where it gets this module from. There's no x.py and no `import x`

        module = import_module(module_path)
        splits = module_path.split(".")
        if splits[-2] != splits[-1]:
            # Skip `package.X.X`, because you already include `package.X.__init__.py` which imports everything from it
            modules.append(module)

        if m.ispkg:
            modules.extend(_get_modules_recursive(module.__path__, package_name))

    return modules


def _find_editable_installs():
    env_lib = re.sub(r"/bin/python.*", "/lib/", sys.executable)
    for item in Path(env_lib).glob("python*/site-packages/katalytic_*.pth"):  # pragma: no cover
        if item.stem not in _pkg_whitelist:
            continue

        # no coverage: because I would have to create an editable install,
        # just to test this functionality
        try:
            yield import_module(item.stem)
        except Exception as e:  # pragma: no cover
            warnings.warn(f"Couldn't import {item.stem!r}\n{_get_stacktrace(e)}")

    for item in Path(__file__).parent.parent.parent.iterdir():  # pragma: no cover
        # no coverage: because I would have to create an editable install,
        # just to test this functionality
        if item.stem not in _pkg_whitelist:
            continue

        if not re.search(r"katalytic_\w+.pth", item.name):
            continue

        try:
            yield import_module(item.stem)
        except Exception as e:  # pragma: no cover
            warnings.warn(f"Couldn't import {item.stem!r}\n{_get_stacktrace(e)}")


def find_functions_marked_with(group):
    """Get a list of functions within the package that belong to a specific group.

    Args:
        group (str):
            The name of the group.

    Returns:
        list:
            A list of tuples containing the function name, the function object, and the groups it belongs to.
            The list is sorted based on the function names.
    """
    functions = []
    for module in get_katalytic_modules():
        for func_name in dir(module):
            f = getattr(module, func_name)
            groups = getattr(f, "__katalytic_marks__", [])
            groups = tuple(g for g in groups if _check(g, group))
            if groups:
                functions.append((func_name, f, groups))

    return sorted(set(functions))


def mark(label):
    """Decorator to mark a function with one or more labels.

    Args:
        label (str):
            The label to mark the function with.

    Returns:
        callable:
            The decorator to mark a function.

    Raises:
        TypeError:
            If the provided label is not a string.
        ValueError:
            If the provided label contains newline characters, tab characters, or consists only of whitespace characters.
    """
    if not isinstance(label, str):
        raise TypeError(f"Only strings are allowed. Got {label!r}")

    if "\n" in label or "\t" in label or re.search(r"^\s*$", label):
        raise ValueError(f"Choose a meaningful label. Got {label!r}")

    def decorator(func):
        pkg = import_module(func.__module__).__package__.split(".")[0]
        if not (pkg in _pkg_whitelist or _is_katalytic_test(func.__module__)):
            raise RuntimeError(f"Only katalytic packages are allowed. Found: {pkg!r}")

        # prepend to maintain the intuitive order (top to bottom)
        func.__katalytic_marks__ = (label, *getattr(func, "__katalytic_marks__", ()))
        return func

    return decorator


@mark("__test_1")
@mark("__test_2")
@mark("__test_300")
def __test():
    pass


@mark("__test_3::a")
@mark("__test_3::b")
@mark("__test_2")
def __test_2():
    pass


_UNDEFINED = object()
__version__, __version_info__ = get_version("katalytic")
