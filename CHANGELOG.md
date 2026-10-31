NEWS for Python X Library

Unreleased
==========

Breaking Changes
----------------

- Python 2, end of life since 2020, is no longer supported. Python 3.3 or newer is required.
- The `six` helpers that modules imported are no longer reachable from them:
  - `Xlib.display.create_unbound_method`
  - `Xlib.ext.xinput.integer_types`
  - `Xlib.protocol.display`: `PY3`, `byte2int`, `indexbytes`
  - `Xlib.protocol.rq`: `PY3`, `binary_type`, `byte2int`, `indexbytes`, `iterbytes`

Typing
------

- The package ships type stubs and a `py.typed` marker (PEP 561). The stubs come from typeshed's `types-python-xlib`, imported with their history (thanks [@Avasam][Avasam], [@AlexWaygood][AlexWaygood], [@srittau][srittau], [@brianschubert][brianschubert], [@hauntsaninja][hauntsaninja], [@jelle-openai][jelle-openai] and [@MestreLion][MestreLion]), and are licensed under Apache-2.0.
- Uninstall `types-python-xlib`: type checkers prefer stub packages over the stubs a package ships, so it would shadow them.
- Compared to `types-python-xlib`, `rq.List` accepts `rq.Str` or any parse-only type with a `parse_binary` method as its type, and `rq.Object` accepts a tuple, dict or `DictWrapper` as its default.
- Compared to `types-python-xlib`, `rq.List` and `rq.FixedList` accept a `ValueField` instance as their type, `rq.FixedList` accepts every type `rq.List` does, and value fields accept `None` as their name. `rq.Field.name` is `str | None` to match, `rq.Object.default` has the type its default parameter accepts, and `rq.Str.pack_value` accepts bytes. `rq.Struct.fields` is a tuple of any length instead of a single field.

Performance
-----------

- Large replies are received much faster, by no longer copying everything received so far on each socket read. A full 3840x2160 `GetImage` on Xvfb went from ~245 ms to ~70 ms.
- Replies and events index bytes directly instead of calling `six` helpers while parsing.
- Minor speedups in keyboard and modifier mapping parsing, and request sending.

Bug Fixes
---------

- `Display.list_fonts_with_info` works on Python 3.
- `Str` fields count UTF-8 bytes in their length prefix, so non-ASCII text and strings of 128 bytes or more no longer corrupt the request. `bytes` values are accepted, and strings over 255 bytes raise `ValueError`.
- Xauthority entries of family `FamilyWild` are matched like libXau does, so connecting still works when the hostname no longer matches the one in the entry, as with Mutter's XWayland (thanks [@barlowa124][barlowa124]).
- Sockets are closed when connecting fails, instead of leaking until garbage collected (thanks [@CristiFati][CristiFati]).
- `unix_connect.old_get_auth` (unused by default) decodes the `xauth list` cookie on Python 3, and calls `xauth` without going through a shell.
- `ResourceDB.insert_file` accepts `str` file names, and closes the file it opens when given a path.
- `Colormap.copy_colormap_and_free` no longer always raises `NameError`.
- `Window.set_wm_colormap_windows` no longer raises `TypeError` on Python 3.
- `Display.keysym_to_keycodes` always returns a list. It used to return a single-use iterator when the keysym was found.
- These `Window` methods default `hints` to `None` instead of a mutable `dict` shared between calls, so passing `hints=None` explicitly works too:
  - `set_wm_normal_hints`
  - `set_wm_hints`
  - `set_wm_state`
  - `set_wm_icon_size`
- `parse_binary_value` always returns its remaining data as `bytes`.
- `import Xlib` imports the submodules listed in `Xlib.__all__`, and `Xlib.ext.__all__` is a list instead of a single-use iterator.
- On Windows, `DISPLAY=:0` connects over TCP to `localhost` instead of raising `AttributeError`, and `unix/:0` raises `DisplayConnectionError`. Elsewhere, the TCP fallback for `:0` connects to `localhost` instead of the empty address.
- When neither `XAUTHORITY` nor `HOME` is set, as is usual on Windows, `.Xauthority` is read from `USERPROFILE` like libXau does, instead of connecting without a cookie.
- On macOS, a `DISPLAY` that names XQuartz's socket connects to that socket. Its protocol was parsed as `None`, so `/tmp/.X11-unix/X<n>` was tried instead.
- On macOS, the launchd socket path XQuartz sets in `DISPLAY` (`/private/tmp/com.apple.launchd.<id>/org.xquartz:0`) no longer raises `DisplayNameError`.
- On macOS, connecting through XQuartz's socket sends the Xauthority cookie. The hostname was looked up as `str` against `bytes` entries, so no cookie matched.
- `rq.DictWrapper` and `rq.Event` no longer define `<` and `>`, which compared the underlying `dict` and so always raised `TypeError`. Comparing them still raises `TypeError`, but now names their own class, and a reflected comparison on the other operand gets the wrapper instead of its `dict` ([python-xlib/python-xlib#253](https://github.com/python-xlib/python-xlib/issues/253)).

Extensions
----------

- Xinerama: `Display.xinerama_get_info` returns the reply instead of `None`.
- Record: `EnableContext` no longer raises `TypeError` when given extra positional arguments.

Examples and utilities
----------------------

- `examples/put_selection.py` answers `TARGETS` requests instead of crashing with `TypeError` on Python 3.
- `examples/xlsatoms.py -n` reports a missing atom instead of creating it, and only catches `BadAtom`, so interrupts and unrelated errors are no longer reported as a missing atom.
- `examples/put_selection.py` reads stdin as bytes, like it reads files.
- `examples/xdamage.py` skips frames that fail to capture instead of crashing, and is executable.
- `examples/dpms.py` exits with an error message when DPMS is unavailable, including on servers without the extension such as VcXsrv, instead of an `AssertionError` or `UnboundLocalError`.
- `examples/threadtest.py` works on Python 3.
- `utils/parsexbug.py` and `utils/tcpbug.py` work on Python 3. `parsexbug.py` is executable, and `tcpbug.py` works under `python -S`.
- `utils/tcpbug.py` works on Windows. It passed stdout to `select.select`, which only accepts sockets there.

Dependencies and packaging
--------------------------

- First release of the fork, published on PyPI as `avasam-python-xlib`. It is a drop-in replacement for `python-xlib`: the import name is still `Xlib`.
- `six` is no longer a dependency (thanks [@a-detiste][a-detiste]). Python 3.8 and newer have no runtime dependencies.
- Python 3.6 and 3.7 depend on the `importlib-metadata` backport, to read `Xlib.__version__`.
- Building no longer needs `setuptools` or `setuptools-scm`.
- Built with `uv_build` from `pyproject.toml`. Building from source needs Python 3.8 or newer.
- Wheels are `py3-none-any`, and the sdist is `.tar.gz`.
- PyPy is tested in CI, on PyPy 3.6 and 3.12.
- macOS (with XQuartz's Xvfb) is tested in CI on Python 3.5 and 3.15, and Windows (with VcXsrv) on Python 3.4 and 3.15.
- The version is declared only in `pyproject.toml`. `Xlib.__version__` reads it from the installed metadata, and is `0+unknown` on Python 3.3 to 3.5 or from an uninstalled source tree.

---

Version 0.33
============

Bug Fixes
---------

- Removed unused imports (thanks [@Avasam][Avasam]).
- Avoid to use fcntl module on some environments (thanks [@i2y][i2y]).
- Change a test behavior for `unix_connect.get_socket` (thanks [@i2y][i2y]).
- Fix accidental data change (thanks [@Avasam][Avasam]).
- Prefer `bool` over `Literal[0, 1, None]` (thanks [@Avasam][Avasam]).
- Change parentheses to brackets in LICENSE (thanks [@mtelka][mtelka]).

---

Version 0.32
============

Bug Fixes
---------

- Use archived link for X documentation resource (thanks [@yaxollum][yaxollum]).
- Fix for auth entry having no display number (thanks [@Majiir][Majiir]).
- Fix return type inconsistency with the `pack_value` for class `Object` (thanks [@allfro][allfro]).
- Rename `add_extension_error` method to `extension_add_error` (thanks [@mattalexx][mattalexx]).

Extensions
--------------------

- screensaver: fix screensaver protocol mismatch (thanks [@yut23][yut23]).
- XRandr: add version 1.5 support for RRSetMonitor RRGetMonitors and RRDeleteMonitors (thanks [@allfro][allfro] and [@jklong][jklong]).

---

Version 0.31
============

Extensions
--------------------

- XInput: add event methods (thanks [@dd4e][dd4e]).

---

Version 0.30
============

Extensions
--------------------

- XResource: first implementation (thanks [@alebastr][alebastr]).
- XRandr: add missing parameters to delete_output_mode function (thanks [@jimmy-loyola][jimmy-loyola]).

---

Version 0.29
============

Extensions
--------------------

- Drawable & XInput: Avoid using array.array.tostring() which wiil be removed in Python 3.9 (thanks [@t-wissmann][t-wissmann]).

---

Version 0.28
============

Extensions
--------------------

- DPMS: Display Power Management Signaling (by [@thiagokokada][thiagokokada])

---

Version 0.27
============

Bug Fixes
---------

- fix TypeError in socket.error exception handling for Python 3.x (by [@t-wissmann][t-wissmann])

Extensions
--------------------

- NV-CONTROL: set offset for all perf levels (by [@Sporif][Sporif])

---

Version 0.26
============

Bug Fixes
---------

- support legacy X servers like RealVNC's one (by [@Gerardwx][Gerardwx])

Extensions
--------------------

- enrich XFixes extension with XFixesSelectionNotify events (by [@acrisci][acrisci])
- add example xfixes-selection-notify.py (by [@acrisci][acrisci])
- fix two issues in NV-CONTROL extension (by [@leinardi][leinardi])
- add method get_clock_info into NV-CONTROL extension (by [@leinardi][leinardi])
- add default client version into Composite extension (by [@jakogut][jakogut])
- add Damage extension with the example (by [@mgarg1][mgarg1] and [@jakogut][jakogut])

---

Version 0.25
============

Bug Fixes
---------

- fix increasing memory usage on display instantiation

NV-CONTROL extension
--------------------

- add first implementation by Roberto Leinardi ([@leinardi][leinardi])

---

Version 0.24
============

Bug Fixes
---------

- fix protocol handling: correctly support explicit Unix
  connections and fix support fox macOS
- improve Python 3 support: fix events sub-code handling
  and possible crashes when unpacking text data
- add support for error handlers to the Composite extension

Misc
----

- fix `xfixes` example
- fix a bunch of typos in the code / documentation

---

Version 0.23
============

Bug Fixes
---------

- fix strings decoding: use Latin-1

---

Version 0.22
============

Bug Fixes
---------

- fix `Display.change_pointer_control` implementation
- fix `Drawable.put_pil_image` implementation

---

Version 0.21
============

Bug Fixes
---------

- fix use under Windows Subsystem for Linux: when DISPLAY does not
  specify a protocol, and the implicit Unix socket connection fails,
  fallback to TCP (mimicking XCB's behavior).

Misc
----

- don't bundle a copy of texi2html to build the HTML documentation,
  but use the currently installed version instead.

---

Version 0.20
============

Bug Fixes
---------

- fix unclosed file in Xauth implementation
- fix support for `Window.set_wm_transient_for`
- fix support for `Drawable.put_image` / `Drawable.get_image`
- use ASCII for decoding strings in Python 3 (same as Python 2)
- fix Python 3 warnings about `array.tostring()` (deprecated)

Misc
----

Improve response processing performance: reduce the number of
`socket.recv` calls needed to receive a full response.

---

Version 0.19
============

Bug Fixes
---------

- don't throw an exception if `$XAUTHFILE` / `~/.Xauthority` is missing
- fix authentication work-around for SSH forwarding under Python 3
- improve `$DISPLAY` handling: support optional protocol prefix, and
  correctly handle `unix:0.0` as `:0.0`

---

Version 0.18
============

Bug Fixes
---------

- fix Python 3 buffer abstraction
- fix interrupted select handling for Python 3.3/3.4
- fix Unix socket support when only an abstract address is available

---

Version 0.17
============

Bug Fixes
---------

- fix Xauth handling when using Python 2 and DISPLAY contains a remote IP
- fix String16 request field handling when using Python 3
- fix RECORD extension and example when using Python 3
- fix handling of properties: use byte strings for all X11 8-bits
  strings, as not all of them are text properties (the window
  getters/setters for `wm_name`, `wm_icon_name`, `wm_class`, and
  `wm_client_machine` still return/expect Unicode strings)

API Changes
-----------

Core:

- new window getter/setter for text properties: `get_full_text_property`
  and `change_text_property`; with automatic conversion to/from Unicode
  when the property type encoding is supported (`STRING` and
  `UTF8_STRING`)

Composite extension:

- support for `GetOverlayWindow` request

---

Version 0.16
============

Licensing
---------

The project is now licensed under the GNU Lesser General Public License
v2.1 or later (see the LICENSE file for details).

Compatibility
-------------

Support for Python versions older than 2.7 has been dropped. Support for
Python 3 (3.3, 3.4 and 3.5) has been added. Note that Python-Xlib now
depends on the six package (>=1.10) for combined Python 2 / 3 support.

API Changes
-----------

With the change of license, and no way to contact the original author of
the SHAPE extension, the code had to be rewritten from scratch. This
resulted in a few minor API changes (see [examples/shapewin.py](examples/shapewin.py)).

Partial support for the SECURITY. XInput, and XFIXES extensions has been
added.

Bug Fixes
---------

- fix RECORD extension
- fixed OS X socket path
- fix handling of generic events
- fix handling of KeymapNotify events
- several fixes for the RandR extension

---

Version 0.15rc1 - 14 Nov 2009
=============================

Improved support for newer versions of Mac OS X, a couple of new
extensions, and several bugfixes.

Composite extension
-------------------

Support for the composite extension, used to implement a composition
manager (added for plcm work in plwm).

By itself this extension is not very useful, it is intended to be used
together with the DAMAGE and XFIXES extensions. Typically you would also
need RENDER or glX or some similar method of creating fancy graphics.

XF86 special function keysyms
-----------------------------

Keysym definitions for special function keys found on modern keyboards,
e.g. raise and lower volume, start specific applications, etc. Have a
look in [Xlib/keysymdef/xf86.py](Xlib/keysymdef/xf86.py) to see what
there are and experiment with xev to see what your keyboard generates.
These definitions aren't brought in by default, so you must do this
after importing `Xlib.XK`:

```python
Xlib.XK.load_keysym_group('xf86')
```

RANDR extension
---------------

The RANDR extension complements XINERAMA as a way of getting data about
the physical screens making up a virtual screen in X. An example of
usage can be found in [examples/xrandr.py](examples/xrandr.py).

---

Version 0.14 - 1 Oct 2007 (trialed as 0.14rc1 on 10 Jun 2007)
=============================================================

A couple of new extensions, a Python 2.5 fix and a couple of aliases
(`Display.get_atom()` now uses the internal cache and added
`Window.raise_window()`). Tabs converted to spaces (SF id: 1559082).

RECORD extension (SF id: 1538663)
---------------------------------

Alex Badea contributed a RECORD extension module, allowing Python Xlib
programs to capture mouse and keyboard events (or all other core or
extension events) easily. A demo is in the examples directory. See
<http://refspecs.freestandards.org/X11/recordlib.pdf> for more
information.

XINERAMA extension
------------------

Mike Meyer contributed a Xinerama extension module, allowing Python Xlib
programs to interrogate the X server about positions and sizes of
multiple screens. Specifications are a bit tricky to find -
<http://sourceforge.net/projects/xinerama/> has some older specs and the
source code of the xorg project (libs & server code) has "definitive"
information.

Python 2.5 fix (SF id: 1623900)
-------------------------------

Bugfix to correct handling of XAuthority file parsing under Python 2.5
causing failed authentication.

---

Version 0.13 - 6 Aug 2006 (trialed as 0.13pre1 on 22 Jul 2006)
==============================================================

A small release to incorporate a number of minor corrections and bug
fixes, including small changes to keysym handling, `.Xauthority`
parsing, several fixes to sending/receiving/flushing data, addition of
`WithdrawnState` to `WMHints`. petli completed documentation for
`Display` objects.

---

Version 0.12 - 29 Mar 2002
==========================

SHAPE extension
---------------

Jeffrey Boser contributed a SHAPE extension module, allowing Python Xlib
programs to use shaped windows. Take a look at examples/shapewin.py for
ideas on how to use it. For more information on shaped windows, see
<http://ftp.x.org/pub/R6.6/xc/doc/hardcopy/Xext/shape.PS.gz>

Python 2.2 fix
--------------

In Python 2.2 `FCNTL.FD_CLOEXEC` has disappeared and `FCNTL` on the whole
is deprecated, so that had to be dealt with to make the Xlib work with
that version.

---

Version 0.11 - 23 Feb 2002
==========================

Regression tests for the protocol definition
--------------------------------------------

Regressions tests have been created for all requests, replies and
events. The tests use PyUnit, and the old resource database test has
been updated to use it too.

A lot of protocol bugfixes
--------------------------

The bugs discovered by the regression tests have been fixed.
Additionally, a subtle bug in the core engine which could cause a
"can't happen"-error has also been found and fixed.

---

Version 0.10 - 16 Dec 2001
==========================

Event bugfix
------------

The xlib failed to parse the type code of events sent from other clients
using `SendEvent`. This has been fixed, adding the field `send_event' to
all event objects.

Event documentation
-------------------

The section "Event Types" in the manual has been written, detailing
all event types in the core protocol. The manual is now ten pages
thicker.

Basic support for GetImage/PutImage
-----------------------------------

The Drawable methods `put_image()` and `get_image()` have been
implemented, but handling image data is still up to the user. There is
however, thanks to Ilpo Nyyssönen, a trivial method `put_pil_image()`
that will work on some combinations of image and drawable depth. It's
not perfect, but it's a start.

---

Version 0.9 - 4 Dec 2001
========================

Documentation improved
----------------------

The documentation has been augmented with a chapter about event
handling, and a chapter listing all X objects and their methods provided
by the library. They are not described in any detail, though.

Keysym handling improved
------------------------

The module `Xlib.XK`, which listed all keysyms, have been split up into
several sub-modules providing different sets of keysyms. By importing
`Xlib.XK` only the miscellany and latin1 sets are loaded, thus removing
some unnecessary clutter.

`Xlib.display.Display` has two new methods (`lookup_string()` and
`rebind_string()`) for translating keysyms into characters.

Small changes to library interface
----------------------------------

The order of the `Xlib.display.Display` method `send_event()` parameters
`event_mask` and propagate has changed.

Some of the class names in `Xlib.protocol.event` have changed, to have
the same name as the corresponding event type constant.

A few bugfixes
--------------

If a display has more than one screen, the default screen was always set
to the highest numbered one, irrespective of what the user specified in
`$DISPLAY`.

Some response attributes in `Xlib.protocol.request` accidentally included
a comma.

---

Version 0.8 - 12 Jan 2001
=========================

Uses distutils
--------------

Python Xlib now uses distutils to make installation and distribution
building easier.

Tested with Python 2.0
----------------------

A few incompatibilities with Python 2.0 has been fixed.

---

Version 0.7 - 8 Jan 2001
========================

Fixed the 64-bit platform fix
------------------------------

As it turns out, the attempted fix for 64-bit platforms in v0.6 didn't
really work. Close study of structmodules.c gave the answer why, and now
it really should work. Yeah.

Optimizations of core protocol engine
-------------------------------------

Python Xlib is now at least 25% faster after the core of the protocol
engine has been rewritten. This is some quite cute code: tailor-made
methods are generated for all structures, resulting in a 650% speed-up
in generating binary data, and a 75% speed-up in parsing binary data.

Interested Python hackers are recommended to take a look at the Struct
class in `Xlib/protocol/rq.py`.

---

Version 0.6 - 29 Dec 2000
=========================

Fix to make python-xlib work on 64-bytes architectures
-------------------------------------------------------

The struct and array modules uses `sizeof(long)` to determine the number
of bytes used when representing the type code 'l'. On Intel and VAX,
this is 32 bits as expected. On Alpha, it's 64 bits. python-xlib now
probes how large each type code is to avoid this problem.

---

Version 0.5 - 28 Dec 2000
=========================

- Functions implemented to get and set all ICCCM WM properties on Window
  objects.

- Keymap cache implemented, with external `Xlib.display.Display` methods
  `keycode_to_keysym`, `keysym_to_keycode`, `keysym_to_keycodes` and
  `refresh_keyboard_mapping`.

- Two utils for debugging X traffic implemented. `utils/tcpbug.py`
  forwards a TCP connection and outputs the communication between the
  client and the server. This output can then be fed into
  `utils/parsexbug.py`, which will output all requests, responses,
  errors and events in a readable format.

---

Version 0.4 - 4 Oct 2000
========================

- Thread support completed, but not really stress-tested yet.

- A framework for handling different platforms has been implemented,
  together with generic Unix code and some simple VMS code.

- Some documentation has been written.

- The usual bunch of bugfixes.

---

Historical ChangeLog
====================

Per-file notes kept between 2000 and 2007, formerly in `Xlib/ChangeLog` and `Xlib/protocol/ChangeLog`. Newest first, paths relative to the repository root.

2007-06-10: Mike Grant <mgg@nobodymuch.org>
--------------------------------------------

- (many files) (mgg): Converted tabs to spaces throughout the codebase, using `reindent.py` (SF id: 1559082).

2007-03-18: Mike Grant <mgg@nobodymuch.org>
--------------------------------------------

- `Xlib/display.py` (mgg): Added a `get_atom` alias that uses the internal cache.
- `Xlib/xobject/drawable.py` (mgg): Added a `raise_window()` alias to the `Window` class.

2007-02-15: Mike Grant <mgg@nobodymuch.org>
--------------------------------------------

- `Xlib/xauth.py` (mgg): Python 2.5 didn't like the way the buffer type was used, resulting in X authorisation failure, so reverted to using slices.

2006-11-22: Mike Grant <mgg@nobodymuch.org>
--------------------------------------------

- `Xlib/ext/record.py`: Addition of RECORD extension by Alex Badea <decampos@users.sourceforge.net>, SF patch id: 1538663 (demo program in `examples/record_demo.py`).

2006-09-20: Mike Meyer <mwm@mired.org>
--------------------------------------

- `Xlib/ext/xinerama.py` (mwm): Addition of Xinerama extension.

2006-07-22: Mike Grant <mgg@nobodymuch.org>
--------------------------------------------

Various typo fixes, general updates.

- `Xlib/protocol/display.py` (mggrant): Fix for SF bug 1219457: flushing was blocking and waiting for a read operation. Added missing `import socket` per SF bug 681511. Fix for SF bugs 1098695 and 1098738: the `recv` variable was being used for more than one thing, renamed one.

The ChangeLog hadn't been maintained since 2002, but some of the more significant comments from CVS logs follow:

- `Xlib/display.py` (petli): Fix bug in `refresh_keyboard_mapping`: ignore modifier and pointer remappings. Plays nice with pydoc. Copied some text from the docs to `__doc__` strings in `Xlib/display.py` so that they appear when you use pydoc. Completed documentation for `Display` objects.
- `Xlib/XK.py` (calroc99): Minor doc string changes. Called `load_keysym_group()` for miscellany and latin1 keysyms, rather than importing the modules.
- `Xlib/keysymdef/*` (calroc99): Small change to keysym loading. Works the same way.
- `Xlib/support/*`, `Xlib/xauth.py`, `Xlib/error.py` (petli): Added `~/.Xauthority` parsing by Python code instead of relying on `/usr/X11R6/bin/xauth`. Not activated yet in all cases yet? Activated in `unix_support.py`.
- `Xlib/xobject/drawable.py` (petli): Fix bugs in definition and method of `GrabButton`/`GrabPointer`.
- `Xlib/protocol/request.py` (petli): Fix bugs in definition and method of `GrabButton`/`GrabPointer`.
- `Xlib/xobject/icccm.py` (petli): Add `WithdrawnState` to `WMHints`.
- `doc/*` (petli): Documentation updates, typos and completing documentation for `Display` objects.

2002-03-30: Peter Liljenberg <peter.liljenberg@esdgkonsult.com>
----------------------------------------------------------------

- `Xlib/support/unix_connect.py`: Handle `fcntl`/`FCNTL` changes in Python 2.2.

2002-03-11: Peter Liljenberg <peter.liljenberg@esdgkonsult.com>
----------------------------------------------------------------

- `Xlib/xobject/drawable.py` (`Drawable.fill_arc`): This should be a `PolyFillArc`.

2002-02-22: Peter Liljenberg <peter.liljenberg@esdgkonsult.com>
----------------------------------------------------------------

- `Xlib/protocol/event.py` (`CirculateNotify`, `CirculateRequest`): These are identical, so subclass the common `Circulate`.

2002-02-13: Peter Liljenberg <peter.liljenberg@esdgkonsult.com>
----------------------------------------------------------------

- `Xlib/protocol/rq.py` (`ValueList.parse_binary_value`): Use `=` both for `calcsize` and unpacking. Caused problems on Alpha.

2002-02-11: Peter Liljenberg <peter.liljenberg@esdgkonsult.com>
----------------------------------------------------------------

- `Xlib/protocol/request.py`:
  - (`GetWindowAttributes`): Rename `class` to `win_class`.
  - (`AllocColorPlanes`): Fix `Pad(4)` to `Pad(8)` in reply.
- `Xlib/protocol/rq.py` (`ReplyLength`): Add a reply length field, for completeness and easier unit test generation.

2002-02-10: Peter Liljenberg <peter.liljenberg@esdgkonsult.com>
----------------------------------------------------------------

- `Xlib/protocol/rq.py`:
  - (`DictWrapper.__cmp__`): Let `DictWrapper` compare with plain dictionaries.
  - (`Event.__init__`): Set `send_event` to 0 when creating new events objects, and allow events to be compared.
  - (`Struct.parse_binary`): Allow `LengthField`s to have a `parse_value` method.
  - (`OddLength.parse_value`): Decode field.
  - (`String16.parse_binary_value`): Handle `OddLength` fields.
  - (`TextElements8.parse_binary_value`): Bugfix: return `values` instead of `v`.
  - (`String8.parse_binary_value`): Parse `String8` with no `LengthOf` field.

2002-02-09: Peter Liljenberg <peter.liljenberg@esdgkonsult.com>
----------------------------------------------------------------

- `Xlib/protocol/rq.py` (`TextElements16`): Bugfix: inherit `TextElements8` instead of `TextElements16`. Found while preparing unit tests, whee.

2002-01-14: Peter Liljenberg <peter.liljenberg@esdgkonsult.com>
----------------------------------------------------------------

- `Xlib/protocol/display.py` (`Display.parse_event_response`): Fix bug reported by Ilpo Nyyssönen, whereby `ReplyRequest`s which generate events (e.g. `get_property` with `delete = 1`) will get dropped when the event is received.

2001-12-14: Peter Liljenberg <peter.liljenberg@esdgkonsult.com>
----------------------------------------------------------------

- `Xlib/protocol/display.py` (`Display.parse_event_response`), `Xlib/protocol/rq.py` (`Event.__init__`): Fixed bug in event type decoding: bit 0-6 is the event type, and bit 7 is set if the event was sent by `SendEvent`.

2001-01-19: Peter Liljenberg <petli@cendio.se>
----------------------------------------------

- `Xlib/XK.py`: Moved all keysyms into separate modules, based on their category. By default only the miscellany and latin1 keysyms are loaded, and other have to be loaded by importing the `Xlib.keysymdef.<category>` module, or calling `load_keysym_group('category')`.
- `Xlib/display.py` (`Display.lookup_string`, `Display.rebind_string`): Functions to translate keysyms to strings, and binding keysyms to new strings.

2001-01-16: Peter Liljenberg <petli@cendio.se>
----------------------------------------------

- `Xlib/xobject/drawable.py` (`Window.send_event`), `Xlib/display.py` (`Display.send_event`): Changed the order of the `event_mask` and `propagate` arguments.
- `Xlib/protocol/event.py`: Changed some class names so that they correspond exactly to the event type constants.

2001-01-10: Peter Liljenberg <petli@cendio.se>
----------------------------------------------

- `Xlib/display.py` (`Display._update_keymap`): The first half of the update algorithm operated on an earlier type of code->sym map than the second half. Stupid, stupid. It would have been nice with a type-checker now.

2001-01-09: Peter Liljenberg <petli@cendio.se>
----------------------------------------------

- `Xlib/display.py` (`Display._update_keymap`): Fixed call to `append` with 1.5.2 semantics, broke in newer Pythons.
- `Xlib/protocol/display.py` (`Display.send_request`): Fixed a call to `append()` with multiple arguments, something that modern Pythons don't allow.

2001-01-04: Peter Liljenberg <petli@cendio.se>
----------------------------------------------

- `Xlib/protocol/rq.py`: The fix for 64-bit platforms didn't work, and close scrutiny of `structmodule.c` shows why: it turns out that `=` translates into `<` or `>`, the one the platform would use. This means `B` is one byte, `H` is two and `L` is four, and no extra alignment, always. `@`, which is the default, selects native number of bytes, which on Alpha means that `L` is eight bytes.

  Now the code goes to pains to ensure that `=` encoding is always used, so _now_ it should work on all platforms. Ahem.

2000-12-29: Peter Liljenberg <petli@cendio.se>
----------------------------------------------

- `Xlib/protocol/rq.py`: Optimizations: replace calls to `Field.get_name()` with access to attribute `name` (`Struct.build_from_args`).
- `Xlib/protocol/rq.py`: Alpha forces us to probe how many bytes each struct code in `bhil` represents, instead of being able to assume that `b` is 1, `h` is 2 and `l` is 4.

2000-12-22: Peter Liljenberg <petli@cendio.se>
----------------------------------------------

- `Xlib/display.py` (`Display.keycode_to_keysym`, `Display.keysym_to_keycode`, `Display.keysym_to_keycodes`, `Display.refresh_keyboard_mapping`, `Display._update_keymap`): Added keymap cache implementation.

2000-12-21: Peter Liljenberg <petli@cendio.se>
----------------------------------------------

- `Xlib/xobject/colormap.py` (`Colormap.alloc_named_color`): Extended to handle `#000000` style color specifications.
- `Xlib/xobject/drawable.py` (`Window.reparent`): Renamed from `reparent_window`.
- `Xlib/display.py` (`Display.set_error_handler`): Added.
- `Xlib/protocol/request.py` (`SetClipRectangles`): Fixed typo (attribute was `rectangels`).

2000-12-20: Peter Liljenberg <petli@cendio.se>
----------------------------------------------

- `Xlib/display.py` (`_BaseDisplay`): Implement a cache of atom names.
- `Xlib/protocol/rq.py`:
  - (`DictWrapper.__setitem__`, `DictWrapper.__delitem__`, `DictWrapper.__setattr__`, `DictWrapper.__delattr__`): Add a few methods to the `DictWrapper`, to make sure that even if attributes are changed, all attributes can be found in the `_data` mapping.
  - (`ValueField.__init__`, `Object.__init__`, `ValueField.pack_value`, `Set.__init__`): Added a default parameter, so that structure elements with a default value can be omitted when calling `build_from_args`.

<!-- Create short-form markdown user links -->
[a-detiste]: https://github.com/a-detiste
[acrisci]: https://github.com/acrisci
[alebastr]: https://github.com/alebastr
[AlexWaygood]: https://github.com/AlexWaygood
[allfro]: https://github.com/allfro
[Avasam]: https://github.com/Avasam
[barlowa124]: https://github.com/barlowa124
[brianschubert]: https://github.com/brianschubert
[CristiFati]: https://github.com/CristiFati
[dd4e]: https://github.com/dd4e
[Gerardwx]: https://github.com/Gerardwx
[hauntsaninja]: https://github.com/hauntsaninja
[i2y]: https://github.com/i2y
[jakogut]: https://github.com/jakogut
[jelle-openai]: https://github.com/jelle-openai
[jimmy-loyola]: https://github.com/jimmy-loyola
[jklong]: https://github.com/jklong
[leinardi]: https://github.com/leinardi
[Majiir]: https://github.com/Majiir
[mattalexx]: https://github.com/mattalexx
[MestreLion]: https://github.com/MestreLion
[mgarg1]: https://github.com/mgarg1
[mtelka]: https://github.com/mtelka
[Sporif]: https://github.com/Sporif
[srittau]: https://github.com/srittau
[t-wissmann]: https://github.com/t-wissmann
[thiagokokada]: https://github.com/thiagokokada
[yaxollum]: https://github.com/yaxollum
[yut23]: https://github.com/yut23
