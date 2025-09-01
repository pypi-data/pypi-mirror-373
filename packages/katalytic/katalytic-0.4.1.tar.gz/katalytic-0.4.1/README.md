# katalytic [![version](https://img.shields.io/pypi/v/katalytic)](https://pypi.org/project/katalytic/) [![tests](https://gitlab.com/katalytic/katalytic/badges/main/pipeline.svg?key_text=tests&key_width=38)](https://gitlab.com/katalytic/katalytic/-/commits/main) [![coverage](https://gitlab.com/katalytic/katalytic/badges/main/coverage.svg)](https://gitlab.com/katalytic/katalytic/-/commits/main) [![docs](https://img.shields.io/readthedocs/katalytic.svg)](https://katalytic.readthedocs.io/en/latest/) [![license: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Don't use in production yet.**
I will likely tweak the function names and the default behaviour a few more times.

We'll take care of the boilerplate, so you can **focus on your problems.**

## Installation

```bash
pip install katalytic

# Include plugins with 3rd-party dependencies
pip install katalytic[all]
```

Plugins with 3rd-party dependencies:

- [katalytic-images](https://gitlab.com/katalytic/katalytic-images)

## Features

### data

- Checks for the structure or properties of data structures
- Convert between different data representations
- Sort or apply map recursively on nested data structures
- Positive and negative front detection
- TODO: Link to tocs

```python
>>> detect_fronts_positive('00101101')
[2, 4, 7]

>>> swap_keys_and_values({'a': 1, 'b': 2, 'c': 3})
{1: 'a', 2: 'b', 3: 'c'}

>>> as_list_of_dicts([['b', 'a'], [1, 2], [3, 4]])
[{'b': 1, 'a': 2}, {'b': 3, 'a': 4}]

>>> flatten_recursive([1, [2, [3, 4], 5], 6])
[1, 2, 3, 4, 5, 6]
```

### files

- Atomic operations
- Load and save files with a uniform interface
- Copy, move, and delete files without searching the docs for the right function
- The functions return the same type as the input (`Path` or `str`)
- TODO: Link to tocs

```python
>>> get_files('/home/user/*bash*', prefix=True)
['/home/user/.bash_history', '/home/user/.bash_logout', '/home/user/.bashrc']

>>> get_files('/home/user/*bash*', prefix=False)
['.bash_history', '.bash_logout', '.bashrc']

>>> get_unique_path('{}.csv')
'/tmp/tmp3s0_ltan/1.csv'
```

### maths

- Calculate the L1 and L2 distance between two vectors
- Clip a value to a minimum or maximum
- Convert bounding boxes between different formats
- Calculate the IoU (Intersection Over Union) between bounding boxes
- TODO: Link to tocs

```python
>>> clip(123, 0, 10)
10
>>> clip(-1, 0, 10)
0

>>> convert_bbox([100, 100, 300, 400], 'xyXY', 'xy_wh')
((100, 100), (200, 300))

>>> box_1 = [100, 100, 300, 400]
>>> box_2 = [50, 150, 250, 100]
>>> intersect_bboxes(box_1, 'xyXY', box_2, 'xywh')
(100, 150, 300, 250)

>>> calc_IoU(box_1, 'xyXY', box_2, 'xywh')
0.3076923076923077
```

### metaprogramming

- Access the functions at any depth of the call stack
- TODO: Link to tocs

```python
    >>> def foo():
    ...     caller = reference_caller_function()
    ...     print(f'{caller.__name__}() called foo()')
    ...
    >>> def bar():
    ...     foo()
    ...
    >>> bar()
    bar() called foo()
```

## Roadmap

- decorators
- regexes
- interactive exploration tools/utilities
- maths
- geometry
- data processing
  - images
  - text
  - tabular
  - structured (e.g. list of dicts \<-> dict of lists)

# Similar projects

- [boltons](https://github.com/mahmoud/boltons)
  - Boltons is a set of over 230 BSD-licensed, pure-Python utilities in the same spirit as — and yet conspicuously missing from — the standard library
- [more-itertools](https://github.com/more-itertools/more-itertools)
  - Python's itertools library is a gem - you can compose elegant solutions for a variety of problems with the functions it provides. In more-itertools we collect additional building blocks, recipes, and routines for working with Python iterables.
- [dateutil](https://github.com/dateutil/dateutil/)
  - The dateutil module provides powerful extensions to the standard datetime module, available in Python.
- [toolz](https://github.com/pytoolz/toolz)
  - A functional standard library for Python.

## Contributing

We appreciate any form of contribution, including but not limited to:

- **Code contributions**: Enhance our repository with your code and tests.
- **Feature suggestions**: Your ideas can shape the future development of our package.
- **Architectural improvements**: Help us optimize our system's design and API.
- **Bug fixes**: Improve user experience by reporting or resolving issues.
- **Documentation**: Help us maintain clear and up-to-date instructions for users.
