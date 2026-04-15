<div align="center">

# Campbells 🥫

A condensed web scraping library.

[Install](#installation) •
[Examples](#examples)

</div>

Adapted from [beautifulsoup4][bs4]'s inner package, then linted, refactored, reduced, and seasoned to taste.

[bs4]: https://beautiful-soup-4.readthedocs.io/

## Development

To run pre-commit checks and tests:

```sh
pre-commit run --all-files && pdm run python -m pytest
```

## Examples

To parse a string as HTML, your recipe should call for `CampbellsSoup`:

```py
from campbells import CampbellsSoup

html_str = "<html><body><p>Hello world!</p></body></html>"
soup = CampbellsSoup(html_str)
```

## Installation

**Campbells** is available on PyPi:

``` bash
pip install campbells
```

The dependencies needed to use `html5lib` and `lxml` parsers are not installed by default.
They can be installed with:

- `pip install campbells[html5lib]` to be able to use
  [html5lib](https://html5lib.readthedocs.io/en/latest/).
  - **Pros:** closest to how browsers parses web pages, very lenient, creates valid HTML5.
  - **Cons:** slowest parser.
- `pip install campbells[lxml]` to be able to use
  [lxml](https://lxml.de/).
  - **Pros:** fastest parser.
  - **Cons:** heavier dependency (C extension).
