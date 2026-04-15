# ossify

**O**pen **S**ource **S**oftware **I**ntelligence **F**or **Y**ou.

Repo maintenance intelligence over your published Python packages. Rules
infer structural signals (tests on CI, trusted publishing, dependency
bots, modernisation drift, commit attribution) — no manual labelling.

## Installation

To install from PyPI:

```
uv pip install ossify-observatory
```

## Quickstart

Set your PyPI username in `src/ossify/defaults.toml` (`[user] pypi_username`),
then:

```bash
uv sync
ossify
```

That runs all stages in order. Each is also a separate entrypoint:
`ossify-discover`, `ossify-pypi`, `ossify-repos`,
`ossify-commits`, `ossify-classify`, `ossify-build`, `ossify-site`.

Each stage is idempotent — re-running only redoes work whose inputs changed.

## Usage

```py
usage: ossify [-h]
              [--only {discover,pypi-json,repos,commits,classify,parquet,site}]
              [--from {discover,pypi-json,repos,commits,classify,parquet,site}]
              [--list]

Open Source Software Intelligence For You.

options:
  -h, --help            show this help message and exit
  --only {discover,pypi-json,repos,commits,classify,parquet,site}
  --from {discover,pypi-json,repos,commits,classify,parquet,site}
  --list

Stages:
  discover   Scrape PyPI user page → package names
  pypi-json  Fetch /pypi/{pkg}/json for each package
  repos      Derive repo set from PyPI metadata
  commits    Fetch commit logs via gh api
  classify   Sparse-clone, run rules, delete clone
  parquet    Compose TOMLs → data/repos.parquet
  site       Build static site from parquet
```

## Layout

- `data/cache/` — fetched HTML, PyPI JSON, commit logs (re-fetchable)
- `data/repos/<owner>__<name>/` — canonical store, one TOML per category
- `data/packages/<pkg>` — symlinks back to the owning repo
- `data/repos.parquet` — all records flattened, one row per repo
- `data/site/` — static site (gitignored)

## Adding a signal

1. Drop a new module in `src/ossify/rules/<category>/<signal>.py`
   exposing `rule(ctx) -> RuleResult | None`.
2. Add a field to the relevant Pydantic model in `src/ossify/models/`.
3. Re-run `ossify-classify`.
