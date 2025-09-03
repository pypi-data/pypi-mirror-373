# Coally

Coally — your Colab Ally. Modular helpers for data tasks in notebooks.  
Explore CSV/XLSX with SQL directly in Google Colab & Drive — no databases, no local setup.

[![PyPI](https://img.shields.io/pypi/v/coally.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/coally.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/coally)][pypi status]
[![License](https://img.shields.io/pypi/l/coally)][license]

[![Read the documentation at https://coally.readthedocs.io/](https://img.shields.io/readthedocs/coally/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/marcoderspace/coally/workflows/Tests/badge.svg)][tests]

[![Tests](https://github.com/marcoderspace/coally/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/marcoderspace/coally/actions/workflows/tests.yml?query=branch%3Amain)

[![Codecov](https://codecov.io/gh/marcoderspace/coally/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

## Features

- `coally-sql`: run ad-hoc SQL over CSV/XLSX directly in Google Colab.

## Requirements

- Python 3.8+

## Installation

You can install _Coally_ via [pip] from [PyPI]:

```bash
pip install coally
```

## Quick start (Colab)

```python
from coally import AllySequelUI, UIOptions

# Full UI: drag & drop CSV/XLSX, run SQL, download result
AllySequelUI.show()
```

## Contributing

Contributions are very welcome. See the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license], _Coally_ is free and open source software.

## Issues

If you encounter any problems, please [file an issue] with details.

---

[pypi status]: https://pypi.org/project/coally/
[read the docs]: https://coally.readthedocs.io/
[tests]: https://github.com/marcoderspace/coally/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/marcoderspace/coally
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[license]: https://github.com/marcoderspace/coally/blob/main/LICENSE
[Contributor Guide]: https://github.com/marcoderspace/coally/blob/main/CONTRIBUTING.md
[file an issue]: https://github.com/marcoderspace/coally/issues
[pip]: https://pip.pypa.io/
