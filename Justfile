default:
    ossify

discover:
    ossify-discover

pypi:
    ossify-pypi

repos:
    ossify-repos

clone:
    ossify-clone

commits:
    ossify-commits

classify:
    ossify-classify

build:
    ossify-build && ossify-site

clean-cache:
    rm -rf data/cache

clean-all:
    rm -rf data

regenerate:
    #!/usr/bin/env -S echo-comment --shell-flags="-e" --color bright-green

    # Wipe derived caches / outputs
    rm -rf data/cache/pypi/packages/
    rm -f data/cache/pypi/users/lmmx.txt
    rm -rf data/cache/commits/
    rm -f data/cache/resolution.toml
    rm -f data/repos.parquet
    rm -rf data/site/
    rm -rf data/packages/ data/repos/

    # Rebuild pipeline
    ossify

    # Run pre-commit suite (non-aliased form)
    prek run --all-files

    # Remove unintended deprioritisation (preserve identity TOMLs)
    just reset-identities

    # Discard working tree noise, leaving staged "good" state
    git restore .

    # Regeneration complete (identity.toml preserved, staged set cleaned)

reset-identities:
    #!/usr/bin/env -S echo-comment --shell-flags="-e" --color bright-green

    # Stage everything except identity.toml (clean selection pass)
    git add .
    git restore --staged $(fd -t f | rg "identity.toml")
