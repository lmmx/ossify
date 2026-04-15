## Release process

- `pre-commit run all-files` or `just` if you want to install taplo, whitespace-format, fd-find etc. locally
- `maturin develop --release`
- `git push`
- `gh run download -p wheel*`
- `mv wheel*/* dist/ && rm -rf wheel* && pdm publish --no-build`
