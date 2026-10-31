#!/bin/sh
# Runs the test suite with coverage on a Python from setup-python, using pip,
# for the Python versions that uv cannot install, on macOS, Windows, and PyPy.
# Usage: legacy-tests.sh <requirements file exported from uv.lock>
set -eux

# Fails on syntax newer than this Python, including in the examples and utilities the tests never import.
# Skips `utils/run_checkers.py`, a script that requires Python 3.11 and newer.
python -m compileall -q -x 'run_checkers\.py' Xlib test examples utils

# Python 3.4.4 on Windows can segfault while pip downloads, so retry on a segfault (exit code 139) only.
pip_install() {
  for attempt in 1 2 3; do
    python -m pip install --disable-pip-version-check "$@" && return
    status=$?
    [ "$status" -eq 139 ] || return "$status"
    echo "::warning::pip segfaulted on attempt $attempt"
  done
  return "$status"
}
# The last pip that supports every legacy Python. Python 3.4.4 bundles pip 7.1.2,
# which predates `--require-hashes` and ignores `Requires-Python`.
pip_install pip==19.1.1
pip_install --require-hashes -r "$1"
python -m coverage run -m unittest -v
python -m coverage report > coverage.txt
python -m coverage html
