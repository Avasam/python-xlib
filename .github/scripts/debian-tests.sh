#!/bin/sh
# Builds and tests this tree with the packaging of Debian's current python-xlib, as Debian does, minus its patches.
# A failure there can get the package removed from Debian testing, see https://bugs.debian.org/1006033 .
# Usage: debian-tests.sh <source tree>
set -eux

source_tree=$1

export DEBIAN_FRONTEND=noninteractive
sed -i 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/debian.sources
apt-get update
apt-get install -y --no-install-recommends autopkgtest build-essential

# The packaging of the latest upload to sid, which is what Debian builds.
mkdir /tmp/packaging
cd /tmp/packaging
apt-get source python-xlib

# `dpkg-buildpackage` writes the packages next to the tree.
mkdir /build
cp -a "$source_tree" /build/python-xlib
rm -rf /build/python-xlib/debian
cp -a /tmp/packaging/python-xlib-*/debian /build/python-xlib/debian
cd /build/python-xlib
echo "Debian packaging version: $(dpkg-parsechangelog --show-field Version)"

# Without Debian's patches, so that a failure points at something to fix here for Debian to need none.
if [ -f debian/patches/series ]; then
    grep -v -e '^#' -e '^ *$' debian/patches/series | while read -r patch _; do
        echo "::notice::Debian still patches python-xlib with $patch"
    done
fi
rm -rf debian/patches

# TODO: Remove once Debian's packaging drops the trailing slashes, or dh-python handles them.
# dh-python names the copy of `test/` after its last path component, which is empty,
# so it skips copying it into the build directory and the build runs no test.
if [ -f debian/pybuild.testfiles ]; then sed -i 's:/$::' debian/pybuild.testfiles; fi

# Fails the build when it runs no test, instead of pybuild's default of ignoring it.
export PYBUILD_TEST_UNITTEST=1

apt-get build-dep -y ./
dpkg-buildpackage --no-sign --build=binary

autopkgtest --no-built-binaries ../*.deb ./ -- null
