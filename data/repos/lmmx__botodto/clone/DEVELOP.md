To set up a development environment, clone this repo and run:

```sh
conda create -n botodto python
conda activate botodto
pip install -e .[dev]
```

This will install the library and typical development dependencies (pytest, mypy etc.),
including `datamodel_code_generator` which is required to generate the SDK DTOs.

There is a tox suite you can run by simply calling `tox` in the main folder.
It uses `tox-conda` because that's how I manage my Python environments.

You can run the test suite on its own with `pytest tests/` (this is faster than the full tox suite
but will not include pre-commit hooks, linting, etc.)

To download all the schemas, totalling 110MB (100MB API schema YAML, 10MB git info), upfront rather than on demand, run

```py
import botodto
botodto.utils.git.oa_repo.clone_repository()
```

This is not the default as that would prevent shipping to resource efficient environments (cloud etc).

You will also need to have AWS configured on your machine. Install with `sudo apt install awscli`
and run `aws configure` to set it up.
