default:
    ossify

pc:
    prek run --all-files

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
