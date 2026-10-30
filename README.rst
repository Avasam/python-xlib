The Python X Library (Avasam's fork)
====================================

|Build Status| |codecov.io|

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

The Python X Library requires Python 3.3 or newer.

The Python X Library will only work on systems that have an X server installed,
such as most Linux distros, but will not work on Windows or MacOS.

Installation
~~~~~~~~~~~~

To install the Python Xlib, run this command:

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
.. _AutoSplit:    https://github.com/Toufool/AutoSplit/
.. _types-python-xlib:
   https://github.com/python/typeshed/tree/main/stubs/python-xlib
.. _uv:           https://docs.astral.sh/uv/

.. |Build Status| image::
   https://github.com/Avasam/python-xlib/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/Avasam/python-xlib/actions/workflows/ci.yml
.. |codecov.io| image::
   https://codecov.io/github/Avasam/python-xlib/graph/badge.svg
   :target: https://codecov.io/github/Avasam/python-xlib
