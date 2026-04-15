<div align="center">

# Chinois 🍵

CSS selector implementation for Bisque and Campbells web scraping libraries.

[Install](#installation) •
[Examples](#examples)

</div>

Adapted from [soupsieve][ss]'s inner package, to remove the hard coupling to Beautiful Soup.

[ss]: https://github.com/facelessuser/soupsieve/

## Installation

**Chinois** is available on PyPi:

``` bash
pip install chinois
```

The dependencies needed to use `bisque` and `campbells` parsing libraries are left to your taste.
They can be installed with:

- `pip install chinois[bisque]` for the bold new flavours of Pydantic model-based parsers in Bisque.
- `pip install chinois[campbells]` for the Campbells parsers, preserving the heritage taste of the Beautiful Soup API.

The dependencies needed to use `html5lib` and `lxml` parsers are not installed by default.
They can be installed with:

- `pip install chinois[html5lib]` to be able to use
  [html5lib](https://html5lib.readthedocs.io/en/latest/).
  - **Pros:** closest to how browsers parses web pages, very lenient, creates valid HTML5.
  - **Cons:** slowest parser.
- `pip install chinois[lxml]` to be able to use
  [lxml](https://lxml.de/).
  - **Pros:** fastest parser.
  - **Cons:** heavier dependency (C extension).
