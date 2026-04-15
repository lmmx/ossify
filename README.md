# ossify

**O**pen **S**ource **S**oftware **I**ntelligence **F**or **Y**ou.

Repo maintenance intelligence over your published Python packages. Rules
infer structural signals (tests on CI, trusted publishing, dependency
bots, modernisation drift, commit attribution) — no manual labelling.

## Quickstart

Set your PyPI username in `src/ossify/defaults.toml` (`[user] pypi_username`),
then:

```bash
uv sync
ossify
```

That runs all stages in order. Each is also a separate entrypoint:
`ossify-discover`, `ossify-pypi`, `ossify-repos`, `ossify-clone`,
`ossify-commits`, `ossify-classify`, `ossify-build`, `ossify-site`.

Each stage is idempotent — re-running only redoes work whose inputs changed.

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
