#
# test/test_examples.py -- run some examples.
#
#    Copyright (C) 2016 Svetlana Filicheva
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

import sys
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import create_autospec, patch

from Xlib import display
from . import Xvfb

examples_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

xvfb = Xvfb()
setUpModule = xvfb.start
tearDownModule = xvfb.stop

def run_example(name, *args):
    """ Returns returncode of example """
    cmd = [sys.executable, os.path.join(examples_folder, name)] + list(args)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = proc.communicate()
    if proc.returncode:
        print(res[1].decode())
    return proc.returncode

class TestExamples(unittest.TestCase):
    """ Run some of examples """

# TODO
#     def test_eventthread(self):
#         """ Run eventthread.py -- Tests multithreaded event handling """
#         self.assertEqual(run_example("eventthread.py"), 0)

    def test_get_selection(self):
        """ Run get_selection.py -- demonstrate getting selections """
        self.assertEqual(run_example("get_selection.py", "PRIMARY"), 0)
        self.assertEqual(run_example("get_selection.py", "SECONDARY"), 0)
        self.assertEqual(run_example("get_selection.py", "CLIPBOARD"), 0)

    def test_put_selection(self):
        """ Run put_selection.py -- demonstrate putting selections, read back with get_selection.py """
        # A private selection, so that clipboard managers do not take it over
        # Unbuffered, since stderr is not line buffered before Python 3.9
        put = subprocess.Popen(
            [sys.executable, "-u", os.path.join(examples_folder, "put_selection.py"), "XLIB_TEST_SELECTION", "UTF8_STRING"],
            stdin=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.addCleanup(put.stderr.close)
        self.addCleanup(put.wait)
        self.addCleanup(put.kill)
        put.stdin.write(b"hello")
        put.stdin.close()
        self.assertIn(b"took ownership", put.stderr.readline())

        get = [sys.executable, os.path.join(examples_folder, "get_selection.py"), "XLIB_TEST_SELECTION"]
        targets = subprocess.check_output(get + ["TARGETS"], stderr=subprocess.DEVNULL, timeout=10)
        self.assertEqual(targets.decode().split(), ["TARGETS", "UTF8_STRING"])
        data = subprocess.check_output(get + ["UTF8_STRING"], stderr=subprocess.DEVNULL, timeout=10)
        self.assertEqual(data, b"hello")

    def test_profilex(self):
        """ Run profilex.py -- program to generate profiling data """
        output_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, output_dir)
        self.assertEqual(run_example("profilex.py", os.path.join(output_dir, "profilex_output")), 0)

# TODO
#     def test_record_demo(self):
#         """ Run record_demo.py -- demonstrate record extension """
#         self.assertEqual(run_example("record_demo.py"), 0)

    def test_security(self):
        """ Run security.py -- demonstrate the SECURITY extension """
        # Some Xvfb builds, such as Alpine 3.4's, leave the SECURITY extension out.
        d = display.Display()
        has_security = d.query_extension('SECURITY') is not None
        d.close()
        if not has_security:
            self.skipTest('X server does not support the SECURITY extension')
        self.assertEqual(run_example("security.py", "--generate"), 0)
        self.assertEqual(run_example("security.py", "--revoke"), 0)

    def test_xfixes(self):
        """ Run xfixes.py -- demonstrate the XFIXES extension """
        self.assertEqual(run_example("xfixes.py"), 0)

    def test_xlsatoms(self):
        """ Run xlsatoms.py -- show list atoms on X server """
        self.assertEqual(run_example("xlsatoms.py"), 0)

    def test_xres(self):
        """ Run xres.py -- demonstrate the X-Resource extension """
        self.assertEqual(run_example("xres.py"), 0)

    def test_dpms_without_extension(self) -> None:
        """ dpms.py exits with a message on a server without DPMS, as VcXsrv """
        # An autospec has no `dpms_*` methods, like a `Display` whose server lacks DPMS
        no_dpms = create_autospec(display.Display, instance=True)
        no_dpms.has_extension.return_value = False
        # Not `runpy.run_path`: on Python 3.3, it returns a copy of the globals of a temporary module,
        # whose teardown sets the originals that `main` looks `DPMSExamples` up in to `None`.
        path = os.path.join(examples_folder, "dpms.py")
        with open(path) as f:
            source = f.read()
        example = {"__name__": "dpms"}
        exec(compile(source, path, "exec"), example)
        with patch("Xlib.display.Display", return_value=no_dpms), self.assertRaises(SystemExit) as cm:
            example["main"]()
        self.assertEqual(cm.exception.code, "DPMS is not supported in your system")


if __name__ == '__main__':
    unittest.main()
