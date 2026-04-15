# aws-step-functions-pydantic

[![CI Status](https://github.com/lmmx/aws-step-functions-pydantic/actions/workflows/master.yml/badge.svg)](https://github.com/lmmx/aws-step-functions-pydantic/actions/workflows/master.yml)
[![Coverage](https://codecov.io/gh/lmmx/aws-step-functions-pydantic/branch/master/graph/badge.svg)](https://codecov.io/github/lmmx/aws-step-functions-pydantic)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Pydantic models for AWS step functions

## Usage

### From Step Function ARN

Use the `from_arn()` class constructor

```py
from aws_sfn_pydantic import StateMachine

sfn = StateMachine.from_arn(state_machine_arn="...")
```

### From JSON

Use the `model_validate_json()` class constructor (Pydantic v2 builtin)

```py
from aws_sfn_pydantic import StateMachine

sfn = StateMachine.model_validate_json("...")
```

### To YAML

Use the `to_yaml()` class constructor, which accepts:

- `indent` (default: 2)
- `level` (default: 0)

```py
print(sfn.model_to_yaml())
```

## Requires

- Python 3.10+

## Installation

```sh
pip install aws-step-functions-pydantic
```

> _aws-step-functions-pydantic_ is available from [PyPI](https://pypi.org/project/aws-step-functions-pydantic), and
> the code is on [GitHub](https://github.com/lmmx/aws-step-functions-pydantic)
