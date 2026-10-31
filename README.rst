The Python X Library (Avasam's fork)
====================================

|Build Status| |Ruff| 

.. <!-- |mypy| |pyright| |ty| -->

`Homepage`_ | `Releases`_ | `Changelog`_ | `Upstream`_

About this fork
~~~~~~~~~~~~~~~

This is a fork of `python-xlib <Upstream_>`_, published on PyPI as
``avasam-python-xlib``. It provides the same ``Xlib`` package and API, so it
works as a drop-in replacement.

My main motivation for maintaining this fork is `AutoSplit`_, which depends on
it.

The goals of this fork are:

- **First-party typing**: the package ships inline type annotations and a
  ``py.typed`` marker (PEP 561). They match or improve upon typeshed's
  `types-python-xlib`_ stubs.
- **Modern infrastructure**: pip, setuptools and Travis CI are replaced by
  `uv`_, ``pyproject.toml`` and GitHub Actions.
- **Performance improvements** and **Bug fixes**.
- **Wheels**: every release is built and published as a wheel alongside the
  source distribution.
- **Wide Python support**: keeping support for Python 3 versions as old as is
  feasible and reasonable.
- **Fewer runtime dependencies**: dropping third-party packages where the
  standard library or a small amount of code suffices.

Copyright
~~~~~~~~~

The main part of the code is

::

    Copyright (C) 2000-2002  Peter Liljenberg

Some contributed code is copyrighted by `the contributors <Contributors_>`_,
in these cases that is indicated in the source files in question.

The Python X Library is released under LGPL v2.1 or later (since 2016),
see the file LICENSE for details. 0.15rc1 and before were released under
GPL v2.

Requirements
~~~~~~~~~~~~

The supported Python versions are set by ``requires-python`` in
`pyproject.toml`_.

The Python X Library needs an X server to connect to: native on Linux and BSD,
`XQuartz`_ on macOS, and an X server such as `VcXsrv`_ or `X410`_ on Windows.
CI tests it on Linux, on macOS with XQuartz's Xvfb, and on Windows with VcXsrv.

Installation
~~~~~~~~~~~~

To install Avasam's fork of the Python Xlib, run this command:

::

    pip install avasam-python-xlib

This fork installs the same ``Xlib`` package as ``python-xlib``, so uninstall
``python-xlib`` first. Also uninstall ``types-python-xlib``: type checkers
prefer stub packages over inline annotations, so the stubs would shadow this
package's own types.

To install from a source checkout, run ``pip install .`` instead.
Building from source needs Python 3.8 or newer.

Alternatively, you can run programs from the distribution directory, or
change the module path in programs.

There's a simple example program, implemented twice using both the
high-level interface and the low-level protocol.

Introduction
~~~~~~~~~~~~

The Python X Library is intended to be a fully functional X client
library for Python programs. It is written entirely in Python, in
contrast to earlier X libraries for Python (the ancient X extension and
the newer plxlib) which were interfaces to the C Xlib.

This is possible to do since X client programs communicate with the X
server via the X protocol. The communication takes place over TCP/IP,
Unix sockets, DECnet or any other streaming network protocol. The C Xlib
is merely an interface to this protocol, providing functions suitable
for a C environment.

There are three advantages of implementing a pure Python library:

-  Integration: The library can make use of the wonderful object system
   in Python, providing an easy-to-use class hierarchy.

-  Portability: The library will be usable on (almost) any computer
   which have Python installed. A C interface could be problematic to
   port to non-Unix systems, such as MS Windows or OpenVMS.

-  Maintainability: It is much easier to develop and debug native Python
   modules than modules written in C.

Documentation
~~~~~~~~~~~~~

The reference manual is not finished by far, but is probably still useful. It
can be `browsed online <https://python-xlib.github.io/>`__ (hosted by upstream).

There are also some `example programs <Examples_>`_ and, of course,
`the standard X11 documentation <https://tronche.com/gui/x/xlib/>`__ applies.

Running the tests
~~~~~~~~~~~~~~~~~

The tests use the standard ``unittest`` discovery. Tests that need a live X
display start their own private ``Xvfb`` server, so ``Xvfb`` must be installed
(the ``xvfb`` package on most distributions), and your own display is never
touched.

::

    uv run -m unittest
    uv run -m unittest -v test.test_xlib_display

The big-endian tests (``test.test_requests_be`` and ``test.test_events_be``)
are skipped on little-endian machines, such as x86 and most ARM systems. To
run them, emulate a big-endian CPU with QEMU and Docker. Register QEMU with
the kernel once (``qemu-user-binfmt`` on Debian and Ubuntu), then run them in
an s390x container::

    docker run --rm --platform linux/s390x -v "$PWD:/src:ro" -w /src python:3.15-alpine \
      python -m unittest test.test_requests_be test.test_events_be

CI runs the whole suite on s390x, for every Python version from 3.4. To do
the same, install ``Xvfb`` in the container first::

    docker run --rm --platform linux/s390x -v "$PWD:/src:ro" -w /src python:3.15-alpine \
      sh -c 'apk add --no-cache xvfb >/dev/null && python -m unittest'


Project status
~~~~~~~~~~~~~~

The low-level protocol is complete, implementing client-side X11R6. The
high-level object oriented interface is also fully functional. It is
possible to write client applications with the library. Currently, the
only real application using Python Xlib is the window manager PLWM,
starting with version 2.0.

There is a resource database implementation, ICCCM support and a
framework for adding X extension code. Several extensions have been
implemented (RECORD, SHAPE, Xinerama, Composite, RANDR, DAMAGE,
Generic Event, SECURITY, XFIXES, XInput, XTEST, NV-CONTROL, DPMS and XRes);
patches for additions are very welcome.

There are most likely still bugs, but the library is at least stable
enough to run PLWM. A continuously bigger part of the library is covered
by regression tests, improving stability.

The documentation is still quite rudimentary, but should be of some help
for people programming with the Xlib. X beginners should first find some
general texts on X. A very good starting point is
http://www.rahul.net/kenton/xsites.html

See the file TODO for a detailed list of what is missing, approximately
ordered by importance.

.. _Homepage:     https://github.com/Avasam/python-xlib
.. _Releases:     https://github.com/Avasam/python-xlib/releases
.. _Changelog:    https://github.com/Avasam/python-xlib/blob/HEAD/CHANGELOG.md
.. _Upstream:     https://github.com/python-xlib/python-xlib
.. _Contributors: https://github.com/Avasam/python-xlib/graphs/contributors
.. _Examples:     https://github.com/Avasam/python-xlib/tree/HEAD/examples
.. _pyproject.toml: https://github.com/Avasam/python-xlib/blob/HEAD/pyproject.toml
.. _AutoSplit:    https://github.com/Toufool/AutoSplit/
.. _types-python-xlib:
   https://github.com/python/typeshed/tree/main/stubs/python-xlib
.. _uv:           https://docs.astral.sh/uv/
.. _XQuartz:      https://www.xquartz.org/
.. _VcXsrv:       https://github.com/marchaesen/vcxsrv
.. _X410:         https://x410.dev/

.. |Build Status| image::
   https://github.com/Avasam/python-xlib/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/Avasam/python-xlib/actions/workflows/ci.yml
.. |Ruff| image::
   https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff
.. |mypy| image:: https://www.mypy-lang.org/static/mypy_badge.svg
   :target: https://mypy-lang.org/
   :alt: Checked with mypy
.. |pyright| image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :target: https://microsoft.github.io/pyright/
   :alt: Checked with pyright
.. |ty| image::
   https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json
   :target: https://github.com/astral-sh/ty
   :alt: ty
