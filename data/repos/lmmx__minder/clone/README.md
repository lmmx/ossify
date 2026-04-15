# Minder

[![Vercel deployment](https://img.shields.io/github/deployments/lmmx/minder/Production?label=vercel&logo=vercel&logoColor=white)](https://vercel.com/deployments/Production)
[![PyPI](https://img.shields.io/pypi/v/minder?logo=python&logoColor=%23cccccc)](https://pypi.org/project/minder)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lmmx/minder/master.svg)](https://results.pre-commit.ci/latest/github/lmmx/minder/master)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/minder.svg)](https://pypi.org/project/minder)

<!-- [![build status](https://github.com/lmmx/minder/actions/workflows/master.yml/badge.svg)](https://github.com/lmmx/minder/actions/workflows/master.yml) -->

Exception guard capture utility library.

## Installation

```sh
pip install minder
```

## Demo

The `Minder` context manager keeps failure modes **contained** with minimal **legibility** cost:

```py
from minder import Minder


def succeed() -> dict:
    with Minder() as guard:
        with guard.duty("winning"):
            guard.result = 100
    return guard.report()


response = succeed()
print(response)
```

```py
{'result': 100, 'success': True}
```

When an error is encountered, we get the same interface.

```py
from minder import Minder


def fail() -> dict:
    with Minder() as guard:
        with guard.duty("greet"):
            print("Hello world")
        with guard.duty("division"):
            guard.result = 1 / 0
    return guard.report()


response = fail()
print(response)
```

```py
Hello world
{'result': {'error': 'division by zero', 'where': 'division'}, 'success': False}
```

In this example we expose a reliable interface of a `result` and `success` boolean.

We could also return `guard` (the `Minder` instance) and handle success/failure at the call site,
but the assumption is we would rather have this prepared for us.
