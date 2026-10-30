#!/bin/sh
# Runs the test suite with coverage inside an official `python:X.Y-alpine` Docker image,
# for Python versions that uv can no longer target.
# Alpine keeps the repositories of old releases online, signed with non expiring keys,
# unlike the Debian releases the EOL Python images are based on.
# Usage: docker-tests.sh <requirements file exported from uv.lock>
set -eux

apk add --no-cache xvfb

pip install --require-hashes -r "$1"
python -W all -m coverage run -m unittest -v
coverage report > coverage.txt
coverage html
