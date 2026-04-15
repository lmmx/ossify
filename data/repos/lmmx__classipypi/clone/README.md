# classipypi

[![PyPI](https://img.shields.io/pypi/v/classipypi?logo=python&logoColor=%23cccccc)](https://pypi.org/project/classipypi)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lmmx/classipypi/master.svg)](https://results.pre-commit.ci/latest/github/lmmx/classipypi/master)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/classipypi.svg)](https://pypi.org/project/classipypi)

<!-- [![build status](https://github.com/lmmx/classipypi/actions/workflows/master.yml/badge.svg)](https://github.com/lmmx/classipypi/actions/workflows/master.yml) -->

Neural PyPI package 'Trove classifier' selector.

## Motivation

PyPI 'Trove classifiers' are used in `setup.py` or `pyproject.toml` files to convey to
PyPI users the conditions under which the package has been used or tested,
the topic of the software, etc. such as

- `Operating System :: POSIX :: Linux`
- `Topic :: Software Development :: Libraries`
- `Intended Audience :: Developers`

## Installation

```py
pip install classipypi
```

## Usage

### `ls`

```
usage: classipypi ls [-h] [-i [INCLUDE ...]] [-e [EXCLUDE ...]] [-t] [-g]

Configure input filtering and output display.

options:
  -h, --help            show this help message and exit
  -i [INCLUDE ...], --include [INCLUDE ...]
                        Strings to filter tags for.
                        (default: [])
  -e [EXCLUDE ...], --exclude [EXCLUDE ...]
                        Strings to filter tags against.
                        (default: [])
  -t, --toml            Whether to display the tags as a TOML-compatible list.
                        (default: False)
  -g, --group           Whether to display tags grouped by section.
                        (default: False)
```

For example, to show the _Development Status_ tags (but skip any with "Alpha" in):

```sh
classipypi ls -i "Development Status" -e Alpha
```

```
Development Status :: 1 - Planning
Development Status :: 4 - Beta
Development Status :: 5 - Production/Stable
Development Status :: 6 - Mature
Development Status :: 7 - Inactive
```

### `sel`

Use `-q` or `--query` to select classifiers based on a description:

```sh
classipypi -q "3D scientific visualisation tool"
```

```
usage: classipypi sel [-h] [-q QUERY] [-s SOURCE] [-t] [-g]

Configure source and y.

options:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        The query string.
                        (default: None)
  -s SOURCE, --source SOURCE
                        The source code.
                        (default: None)
  -t, --toml            Whether to display the tags as a TOML-compatible list.
                        (default: False)
  -g, --group           Whether to display tags grouped by section.
                        (default: False)
```

Use `-s` or `--source` to select classifiers based on source code:

```sh
classipypi --source ./local_package_repo/
```


## Development

- To set up pre-commit hooks (to keep the CI bot happy) run `pre-commit install-hooks` so all git
  commits trigger the pre-commit checks. I use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
  This runs `black`, `flake8`, `autopep8`, `pyupgrade`, etc.

- To set up a dev env, I first create a new conda environment and use it in PDM with `which python > .pdm-python`.
  To use `virtualenv` environment instead of conda, skip that. Run `pdm install` and a `.venv` will be created if no
  Python binary path is found in `.pdm-python`.

- To run tests, run `pdm run python -m pytest` and the PDM environment will be used to run the test suite.
