#!/bin/sh
# Runs the test suite with coverage inside an official `python:X.Y-alpine` Docker image,
# for Python versions that uv can no longer target, and for CPU architectures that need QEMU.
# Alpine keeps the repositories of old releases online, signed with non expiring keys,
# unlike the Debian releases the EOL Python images are based on.
# Usage: docker-tests.sh <requirements file exported from uv.lock>
set -eux

# Fails on syntax newer than this Python, including in the examples and utilities the tests never import.
if python -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
    python -m compileall -q Xlib test examples utils
else
    # Skips `utils/run_checkers.py`, a script that requires Python 3.11 and newer.
    python -m compileall -q -x 'run_checkers\.py' Xlib test examples utils
fi

apk add --no-cache xvfb

# The images ship the pip of their era, and newer pip drops support for these Pythons.
pip install --disable-pip-version-check --require-hashes -r "$1"
coverage run -m unittest -v
coverage report > coverage.txt
coverage html
