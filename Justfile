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

    # Stage everything first
    git add -A

    # Preserve identity.toml files exactly as in HEAD when they were modified
    git diff --cached --name-only -z \
    | while IFS= read -r -d '' f; do
        case "$f" in
            *identity.toml)
                continue
                ;;
        esac

        head_blob=$(git rev-parse "HEAD:$f" 2>/dev/null) || continue
        index_entry=$(git ls-files -s -- "$f")
        [ -z "$index_entry" ] && continue

        mode=$(echo "$index_entry" | awk '{print $1}')

        new_blob=$(
            {
                git show "HEAD:$f"
            } | git hash-object -w --stdin
        )

        git update-index --cacheinfo "$mode,$new_blob,$f"
    done

    # Re-stage everything except identity.toml (clean selection pass)
    fd -t f . data \
    | rg -v "identity.toml$" \
    | xargs git add

    # Discard working tree noise, leaving staged "good" state
    git restore .

    # Regeneration complete (identity.toml preserved, staged set cleaned)
