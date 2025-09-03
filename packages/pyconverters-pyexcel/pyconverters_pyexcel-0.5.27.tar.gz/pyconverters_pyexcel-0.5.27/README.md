# pyconverters_pyexcel

[![license](https://img.shields.io/github/license/oterrier/pyconverters_pyexcel)](https://github.com/oterrier/pyconverters_pyexcel/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyconverters_pyexcel/workflows/tests/badge.svg)](https://github.com/oterrier/pyconverters_pyexcel/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyconverters_pyexcel)](https://codecov.io/gh/oterrier/pyconverters_pyexcel)
[![docs](https://img.shields.io/readthedocs/pyconverters_pyexcel)](https://pyconverters_pyexcel.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyconverters_pyexcel)](https://pypi.org/project/pyconverters_pyexcel/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyconverters_pyexcel)](https://pypi.org/project/pyconverters_pyexcel/)

Convert OCRized PDF to text using [PyWord](https://github.com/pyexcel/PyWord)

## Installation

You can simply `pip install pyconverters_pyexcel`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyconverters_pyexcel
```

### Running the test suite

You can run the full test suite against all supported versions of Python (3.8) with:

```
tox
```

### Building the documentation

You can build the HTML documentation with:

```
tox -e docs
```

The built documentation is available at `docs/_build/index.html.
