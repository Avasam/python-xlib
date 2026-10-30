# Xlib.__init__ -- glue for Xlib package
#
#    Copyright (C) 2000-2002 Peter Liljenberg <petli@ctrl-c.liu.se>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

from . import XK, X, Xatom, Xcursorfont, Xutil, display, error, rdb



def _get_version_string():
    # The version is only declared in pyproject.toml, so read it from the installed metadata.
    import sys
    if sys.version_info >= (3, 8):
        from importlib.metadata import PackageNotFoundError, version
    else:
        try:
            # Backport, only a dependency on Python 3.6 and 3.7
            from importlib_metadata import PackageNotFoundError, version  # type: ignore[import-not-found]
        except ImportError:
            return '0+unknown'
    try:
        return version('python-xlib')
    except PackageNotFoundError:
        # Running from an uninstalled source tree
        return '0+unknown'


def _split_version(version_string):
    import re
    release = re.match(r'\d+(\.\d+)*', version_string).group()
    return tuple(map(int, release.split('.'))), version_string[len(release):]


__version_string__ = _get_version_string()

__version__, __version_extra__ = _split_version(__version_string__)

__all__ = [
    'X',
    'XK',
    'Xatom',
    'Xcursorfont',
    'Xutil',
    'display',
    'error',
    'rdb',
    # Explicitly exclude threaded, so that it isn't imported by
    #  from Xlib import *
    ]
