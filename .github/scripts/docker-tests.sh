#!/bin/sh
# Runs the test suite with coverage inside an official `python:X.Y-alpine` Docker image,
# for Python versions that uv can no longer target, and for CPU architectures that need QEMU.
# Alpine keeps the repositories of old releases online, signed with non expiring keys,
# unlike the Debian releases the EOL Python images are based on.
# Usage: docker-tests.sh <requirements file exported from uv.lock>
set -eux

# Fails on syntax newer than this Python, including in the examples and utilities the tests never import.
python -m compileall -q Xlib test examples utils

apk add --no-cache xvfb

pip install --require-hashes -r "$1"
coverage run -m unittest -v
coverage report > coverage.txt
coverage html
